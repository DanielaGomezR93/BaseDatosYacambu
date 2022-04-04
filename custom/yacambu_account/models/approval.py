from odoo import api, fields, models

CATEGORY_SELECTION = [
    ('required', 'Requerido'),
    ('optional', 'Opcional'),
    ('no', 'Ninguno')]


class ApprovalRequest(models.Model):
    _inherit = "approval.request"

    requesting_unit = fields.Many2one(
        "account.analytic.account",
        string="Unidad Solicitante")
    has_requesting_unit = fields.Selection(related="category_id.has_requesting_unit")


class ApprovalCategory(models.Model):
    _inherit = "approval.category"

    has_requesting_unit = fields.Selection(
        CATEGORY_SELECTION,
        string="Tiene Unidad Solicitante",
        default="no", required=True)


class ApprovalProductLine(models.Model):
    _inherit = "approval.product.line"

    property_account_expense_id = fields.Many2one(
        "account.account",
        string="Cuenta de gasto",
        compute="_compute_property_account_expense_id")

    @api.depends("product_id")
    def _compute_property_account_expense_id(self):
        self.property_account_expense_id = False
        for line in self:
            line.property_account_expense_id = line.product_id.product_tmpl_id.get_product_accounts()["expense"]
