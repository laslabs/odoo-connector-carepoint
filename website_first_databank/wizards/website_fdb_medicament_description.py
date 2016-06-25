# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields

from openerp.addons.first_databank.models.fdb_pem_moe import TYPES


class WebsiteFdbMedicamentDescription(models.TransientModel):
    _name = 'website.fdb.medicament.description'
    _description = 'Website Fdb Medicament Description'

    medicament_id = fields.Many2one(
        string='Medicament',
        comodel_name='medical.medicament',
        default=lambda s: s._default_medicament_id(),
        readonly=True,
    )
    gcn_id = fields.Many2one(
        comodel_name='medical.medicament.gcn',
        related='medicament_id.gcn_id',
        readonly=True,
    )
    monograph_id = fields.Many2one(
        string='Monograph',
        comodel_name='fdb.pem.mogc',
        default=lambda s: s._default_monograph_id(),
        domain="[('gcn_id', '=', gcn_id)]",
    )
    template_id = fields.Many2one(
        string='Template',
        comodel_name='ir.ui.view',
        required=True,
        default=lambda s: s._default_template_id(),
    )
    monograph_html = fields.Html()

    @api.model
    def _default_medicament_id(self):
        model = 'medical.medicament'
        if self.env.context.get('active_model') != 'medical.medicament':
            return
        return self.env.context['active_id']

    @api.model
    def _default_monograph_id(self):
        medicament_id = self.env['medical.medicament'].browse(
            self._default_medicament_id()
        )
        fdb_gcn_id = self.env['fdb.gcn'].search([
            ('gcn_id', '=', medicament_id.gcn_id.id),
        ],
            limit=1,
        )
        if not fdb_gcn_id.monograph_ids:
            return
        return fdb_gcn_id.monograph_ids[0].id

    @api.model
    def _default_template_id(self):
        template_id = self.env.ref(
            'website_first_databank.website_medicament_description'
        )
        return template_id.id

    @api.multi
    @api.onchange('template_id')
    def _onchange_template_id(self):
        self._render_save()

    @api.multi
    def sync_description(self):
        """ Sync the product website description from FDB """
        for rec_id in self:
            rec_id.medicament_id.product_id.website_description = \
                rec_id.monograph_html

    @api.multi
    def _render_save(self):
        for rec_id in self:
            rec_id.monograph_html = rec_id._render()

    @api.multi
    def _render(self):
        return self.template_id.render(
            self._get_template_values(),
            engine='ir.qweb',
        )

    @api.multi
    def _get_template_values(self):
        """ Return values to inject in Monograph template
        Use this method to add additional attributes via child classes
        """
        self.ensure_one()
        return {
            'medicament': self.medicament_id,
            'monograph': self.monograph_id,
            'sections': self.monograph_id._get_sections_dict(),
            'section_headers': dict((k, v) for k, v in TYPES),
        }