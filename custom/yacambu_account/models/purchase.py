from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    property_account_expense_id = fields.Many2one(
        "account.account",
        string="Cuenta de gasto",
        compute="_compute_property_account_expense_id")

    @api.depends("product_id")
    def _compute_property_account_expense_id(self):
        self.property_account_expense_id = False
        for line in self:
            line.property_account_expense_id = line.product_id.product_tmpl_id.get_product_accounts()["expense"]
