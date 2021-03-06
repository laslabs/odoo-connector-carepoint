# -*- coding: utf-8 -*-
# Copyright 2015-2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models, fields, api
from odoo.addons.connector.connector import ConnectorUnit
from odoo.addons.connector.unit.mapper import (mapping,
                                               only_create,
                                               )
from ..unit.backend_adapter import CarepointCRUDAdapter
from ..backend import carepoint
from ..unit.import_synchronizer import DelayedBatchImporter

from .address_abstract import (CarepointAddressAbstractImportMapper,
                               CarepointAddressAbstractImporter,
                               CarepointAddressAbstractExportMapper,
                               CarepointAddressAbstractExporter,
                               )

_logger = logging.getLogger(__name__)


class CarepointAddressPatient(models.Model):
    """ Adds the ``One2many`` relation to the Carepoint bindings
    (``carepoint_bind_ids``)
    """
    _name = 'carepoint.address.patient'
    _inherit = 'carepoint.address.abstract'
    _description = 'Carepoint Address Patient'

    carepoint_bind_ids = fields.One2many(
        comodel_name='carepoint.carepoint.address.patient',
        inverse_name='odoo_id',
        string='Carepoint Bindings',
    )

    @api.model
    def _default_res_model(self):
        """ It returns the res model. """
        return 'medical.patient'


class CarepointCarepointAddressPatient(models.Model):
    """ Binding Model for the Carepoint Address Patient """
    _name = 'carepoint.carepoint.address.patient'
    _inherit = 'carepoint.binding'
    _inherits = {'carepoint.address.patient': 'odoo_id'}
    _description = 'Carepoint Address Patient Many2Many Rel'
    _cp_lib = 'patient_address'  # Name of model in Carepoint lib (snake_case)

    odoo_id = fields.Many2one(
        comodel_name='carepoint.address.patient',
        string='Company',
        required=True,
        ondelete='cascade'
    )


@carepoint
class CarepointAddressPatientAdapter(CarepointCRUDAdapter):
    """ Backend Adapter for the Carepoint Address Patient """
    _model_name = 'carepoint.carepoint.address.patient'


@carepoint
class CarepointAddressPatientBatchImporter(DelayedBatchImporter):
    """ Import the Carepoint Address Patients.
    For every address in the list, a delayed job is created.
    """
    _model_name = ['carepoint.carepoint.address.patient']


@carepoint
class CarepointAddressPatientImportMapper(
    CarepointAddressAbstractImportMapper,
):
    _model_name = 'carepoint.carepoint.address.patient'

    @mapping
    @only_create
    def partner_id(self, record):
        """ It returns either the commercial partner or parent & defaults """
        binder = self.binder_for('carepoint.medical.patient')
        patient_id = binder.to_odoo(record['pat_id'], browse=True)
        _sup = super(CarepointAddressPatientImportMapper, self)
        return _sup.partner_id(
            record, patient_id,
        )

    @mapping
    @only_create
    def res_model_and_id(self, record):
        binder = self.binder_for('carepoint.medical.patient')
        patient_id = binder.to_odoo(record['pat_id'], browse=True)
        _sup = super(CarepointAddressPatientImportMapper, self)
        return _sup.res_model_and_id(
            record, patient_id,
        )

    @mapping
    def carepoint_id(self, record):
        return {'carepoint_id': '%d,%d' % (record['pat_id'],
                                           record['addr_id'])}


@carepoint
class CarepointAddressPatientImporter(
    CarepointAddressAbstractImporter,
):
    _model_name = ['carepoint.carepoint.address.patient']
    _base_mapper = CarepointAddressPatientImportMapper

    def _import_dependencies(self):
        """ Import depends for record """
        super(CarepointAddressPatientImporter, self)._import_dependencies()
        self._import_dependency(self.carepoint_record['pat_id'],
                                'carepoint.medical.patient')


@carepoint
class CarepointAddressPatientUnit(ConnectorUnit):
    _model_name = 'carepoint.carepoint.address.patient'

    def _import_addresses(self, patient_id, partner_binding):
        adapter = self.unit_for(CarepointCRUDAdapter)
        importer = self.unit_for(CarepointAddressPatientImporter)
        address_ids = adapter.search(pat_id=patient_id)
        for address_id in address_ids:
            importer.run(address_id)


@carepoint
class CarepointAddressPatientExportMapper(
    CarepointAddressAbstractExportMapper
):
    _model_name = 'carepoint.carepoint.address.patient'

    @mapping
    def static_defaults(self, binding):
        sup = super(CarepointAddressPatientExportMapper, self)
        return sup.static_defaults(binding, 'home')

    @mapping
    def pat_id(self, binding):
        binder = self.binder_for('carepoint.medical.patient')
        rec_id = binder.to_backend(binding.res_id)
        return {'pat_id': rec_id}


@carepoint
class CarepointAddressPatientExporter(
    CarepointAddressAbstractExporter
):
    _model_name = 'carepoint.carepoint.address.patient'
    _base_mapper = CarepointAddressPatientExportMapper
