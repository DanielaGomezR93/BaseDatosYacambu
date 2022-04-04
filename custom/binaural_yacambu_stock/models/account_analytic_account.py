from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    stock_location_id = fields.Many2one("stock.location", string="Ubicación")

    def action_create_location_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Crear Ubicación",
            "res_model": "stock.location.create.wizard",
            "target": "new",
            "view_id": self.env.ref("binaural_yacambu_stock.view_stock_location_create_wizard").id,
            "view_mode": "form",
            "context": {
                "default_account_analytic_account_id": self.id,
                "default_name": self.name,
                "default_partner_id": self.partner_id.id
            }
        }
