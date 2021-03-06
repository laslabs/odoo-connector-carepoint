# -*- coding: utf-8 -*-
# Copyright 2015-2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock

from odoo.addons.connector_carepoint.models import carepoint_store

from ..common import SetUpCarepointBase


class EndTestException(Exception):
    pass


class CarepointStoreTestBase(SetUpCarepointBase):

    def setUp(self):
        super(CarepointStoreTestBase, self).setUp()
        self.model = 'carepoint.carepoint.store'
        self.mock_env = self.get_carepoint_helper(
            self.model
        )
        self.record = {
            'name': 'Test Pharmacy Name',
            'store_id': 123,
        }


class TestCarepointStoreImportMapper(CarepointStoreTestBase):

    def setUp(self):
        super(TestCarepointStoreImportMapper, self).setUp()
        self.Unit = carepoint_store.CarepointStoreImportMapper
        self.unit = self.Unit(self.mock_env)

    def test_odoo_id_store(self):
        """ It should return odoo_id of pharmacies with same name """
        expect = self.env['carepoint.store'].create({
            'name': self.record['name'],
        })
        res = self.unit.odoo_id(self.record)
        expect = {'odoo_id': expect.id}
        self.assertDictEqual(expect, res)

    def test_odoo_id_pharmacy(self):
        """ It should return new carepoint.store for pharmacy w/ same name """
        expect = self.env['medical.pharmacy'].create({
            'name': self.record['name'],
        })
        rec = self.unit.odoo_id(self.record)
        store = self.env['carepoint.store'].browse(rec['odoo_id'])
        self.assertEqual(expect.id, store.pharmacy_id.id)

    def test_parent_id(self):
        """ It should return id of backend_record company's partner """
        res = self.unit.parent_id(self.record)
        expect = {
            'parent_id':
                self.unit.backend_record.company_id.partner_id.id,
        }
        self.assertDictEqual(expect, res)

    def test_warehouse_id_get_binder(self):
        """ It should get binder for prescription line """
        with mock.patch.object(self.unit, 'binder_for'):
            self.unit.binder_for.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self.unit.warehouse_id(self.record)
            self.unit.binder_for.assert_called_once_with(
                'carepoint.stock.warehouse'
            )

    def test_warehouse_id_to_odoo(self):
        """ It should get Odoo record for rx """
        with mock.patch.object(self.unit, 'binder_for'):
            self.unit.binder_for().to_odoo.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self.unit.warehouse_id(self.record)
            self.unit.binder_for().to_odoo.assert_called_once_with(
                self.record['store_id'],
            )

    def test_warehouse_id_return(self):
        """ It should return formatted warehouse_id """
        with mock.patch.object(self.unit, 'binder_for'):
            res = self.unit.warehouse_id(self.record)
            expect = self.unit.binder_for().to_odoo()
            self.assertDictEqual({'warehouse_id': expect}, res)

    def test_carepoint_id(self):
        """ It should return correct attribute """
        expect = 6789
        self.record['store_id'] = expect
        res = self.unit.carepoint_id(self.record)
        expect = {'carepoint_id': expect}
        self.assertDictEqual(expect, res)


class TestCarepointStoreImporter(CarepointStoreTestBase):

    def setUp(self):
        super(TestCarepointStoreImporter, self).setUp()
        self.Unit = carepoint_store.CarepointStoreImporter
        self.unit = self.Unit(self.mock_env)
        self.unit.carepoint_record = self.record

    def test_after_import_warehouse(self):
        """ It should import all depedencies """
        expect = mock.MagicMock()
        with mock.patch.object(self.unit, '_import_dependency') as mk:
            mk.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self.unit._after_import(expect)
            mk.assert_has_calls([
                mock.call(
                    expect.carepoint_id,
                    'carepoint.stock.warehouse',
                ),
            ])

    def test_after_import_get_binder(self):
        """ It should get binder for warehouse """
        expect = mock.MagicMock()
        with mock.patch.object(self.unit, 'binder_for'):
            self.unit.binder_for.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self.unit._after_import(expect)
            self.unit.binder_for.assert_called_once_with(
                'carepoint.stock.warehouse'
            )

    def test_after_import_to_odoo(self):
        """ It should get Odoo record for warehouse """
        expect = mock.MagicMock()
        with mock.patch.object(self.unit, 'binder_for'):
            self.unit.binder_for().to_odoo.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                self.unit._after_import(expect)
            self.unit.binder_for().to_odoo.assert_called_once_with(
                expect.carepoint_id,
            )

    def test_after_import_write(self):
        """ It should write warehouse to binding """
        expect = mock.MagicMock()
        with mock.patch.object(self.unit, 'binder_for'):
            self.unit._after_import(expect)
            expect.write.assert_called_once_with({
                'warehouse_id': self.unit.binder_for().to_odoo(),
            })
