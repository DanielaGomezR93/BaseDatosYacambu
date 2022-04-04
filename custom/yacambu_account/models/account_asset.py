from odoo import api, fields, models


class AccountAsset(models.Model):
    _inherit = "account.asset"

    account_move_id = fields.Many2one("account.move", string="Factura de Proveedor")
