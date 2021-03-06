# -*- coding: utf-8 -*-
# Copyright 2015-2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock

from odoo.addons.connector_carepoint.models import phone_organization

from ...unit.backend_adapter import CarepointCRUDAdapter

from ..common import SetUpCarepointBase


_file = 'odoo.addons.connector_carepoint.models.phone_organization'


class EndTestException(Exception):
    pass


class PhoneOrganizationTestBase(SetUpCarepointBase):

    def setUp(self):
        super(PhoneOrganizationTestBase, self).setUp()
        self.model = 'carepoint.phone.organization'
        self.mock_env = self.get_carepoint_helper(
            self.model
        )
        self.record = {
            'org_id': 1,
            'phone_id': 2,
        }


class TestPhoneOrganizationImportMapper(PhoneOrganizationTestBase):

    def setUp(self):
        super(TestPhoneOrganizationImportMapper, self).setUp()
        self.Unit = \
            phone_organization.CarepointPhoneOrganizationImportMapper
        self.unit = self.Unit(self.mock_env)

    def test_partner_id_get_binder(self):
        """ It should get binder for organization """
        with mock.patch.object(self.unit, 'binder_for'):
            self.unit.binder_for.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self.unit.partner_id(self.record)
            self.unit.binder_for.assert_called_once_with(
                'carepoint.medical.organization'
            )

    def test_partner_id_to_odoo(self):
        """ It should get Odoo record for organization """
        with mock.patch.object(self.unit, 'binder_for'):
            self.unit.binder_for().to_odoo.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self.unit.partner_id(self.record)
            self.unit.binder_for().to_odoo.assert_called_once_with(
                self.record['org_id'], browse=True,
            )

    def test_carepoint_id(self):
        """ It should return correct attribute """
        res = self.unit.carepoint_id(self.record)
        expect = {
            'carepoint_id': '%d,%d' % (
                self.record['org_id'],
                self.record['phone_id'],
            ),
        }
        self.assertDictEqual(expect, res)


class TestPhoneOrganizationImporter(PhoneOrganizationTestBase):

    def setUp(self):
        super(TestPhoneOrganizationImporter, self).setUp()
        self.Unit = phone_organization.CarepointPhoneOrganizationImporter
        self.unit = self.Unit(self.mock_env)
        self.unit.carepoint_record = self.record

    def test_import_dependencies_import(self):
        """ It should import all dependencies """
        with mock.patch.object(self.unit, '_import_dependency') as mk:
            self.unit._import_dependencies()
            mk.assert_has_calls([
                mock.call(
                    self.record['org_id'],
                    'carepoint.medical.organization',
                ),
            ])


class TestCarepointPhoneOrganizationUnit(PhoneOrganizationTestBase):

    def setUp(self):
        super(TestCarepointPhoneOrganizationUnit, self).setUp()
        self.Unit = phone_organization.CarepointPhoneOrganizationUnit
        self.unit = self.Unit(self.mock_env)

    def test_import_phones_unit(self):
        """ It should get units for adapter and importer """
        with mock.patch.object(self.unit, 'unit_for') as mk:
            mk.side_effect = [None, EndTestException]
            with self.assertRaises(EndTestException):
                self.unit._import_phones(None, None)
            mk.assert_has_calls([
                mock.call(CarepointCRUDAdapter),
                mock.call(
                    phone_organization.CarepointPhoneOrganizationImporter,
                ),
            ])

    def test_import_phones_search(self):
        """ It should search adapter for filters """
        organization = mock.MagicMock()
        with mock.patch.object(self.unit, 'unit_for') as mk:
            self.unit._import_phones(organization, None)
            mk().search.assert_called_once_with(
                org_id=organization,
            )

    def test_import_phones_import(self):
        """ It should run importer on search results """
        expect = mock.MagicMock()
        with mock.patch.object(self.unit, 'unit_for') as mk:
            mk().search.return_value = [expect]
            self.unit._import_phones(1, None)
            mk().run.assert_called_once_with(expect)


class TestPhoneOrganizationExportMapper(PhoneOrganizationTestBase):

    def setUp(self):
        super(TestPhoneOrganizationExportMapper, self).setUp()
        self.Unit = \
            phone_organization.CarepointPhoneOrganizationExportMapper
        self.unit = self.Unit(self.mock_env)
        self.record = mock.MagicMock()

    def test_org_id_get_binder(self):
        """ It should get binder for prescription line """
        with mock.patch.object(self.unit, 'binder_for'):
            self.unit.binder_for.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self.unit.org_id(self.record)
            self.unit.binder_for.assert_called_once_with(
                'carepoint.carepoint.organization'
            )

    def test_org_id_to_backend(self):
        """ It should get backend record for rx """
        with mock.patch.object(self.unit, 'binder_for'):
            self.unit.binder_for().to_backend.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self.unit.org_id(self.record)
            self.unit.binder_for().to_backend.assert_called_once_with(
                self.record.res_id,
            )

    def test_org_id_return(self):
        """ It should return formatted org_id """
        with mock.patch.object(self.unit, 'binder_for'):
            res = self.unit.org_id(self.record)
            expect = self.unit.binder_for().to_backend()
            self.assertDictEqual({'org_id': expect}, res)
