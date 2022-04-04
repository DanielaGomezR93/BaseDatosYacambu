import logging
from odoo.tests.common import Form, SavepointCase
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tools import float_compare
_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class StockWarehouseCreateWizardTestCase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(StockWarehouseCreateWizardTestCase, cls).setUpClass()

        record = cls.env["account.analytic.account"]
        cls.analytic_account = record.create({
            "name": "Cuenta Prueba",
            "partner_id": cls.env.user.company_id.id
        })

    def test_wizard_activation(self):
        """
        Probar que el wizard de creacion de almacen se
        activa correctamente desde la cuenta analitica.
        """
        wizard = self.analytic_account.action_create_warehouse_wizard()
        self.assertEqual(self.analytic_account.name, wizard["context"]["default_name"])
        self.assertEqual(self.analytic_account.partner_id.id, wizard["context"]["default_partner_id"])

    def test_stock_warehouse_creation_through_wizard(self):
        """
        Probar la accion de crear un almacen mediante el wizard de creacion de almacen.
        """
        record = self.env["stock.warehouse.create.wizard"]
        wizard = record.create({
            "name": self.analytic_account.name,
            "partner_id": self.analytic_account.partner_id.id,
            "code": "Prueba Nombre Corto"
        })
        warehouse_form = wizard.action_create_stock_warehouse()
        warehouse_record = self.env["stock.warehouse"].search([("id", '=', warehouse_form.id)])
        self.assertEqual(warehouse_form.name, warehouse_record.name)
        self.assertEqual(warehouse_form.code, warehouse_record.code)
        self.assertEqual(warehouse_form.partner_id, warehouse_record.partner_id)

