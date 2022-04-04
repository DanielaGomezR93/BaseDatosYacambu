from odoo import api, fields, models
from odoo.tests.common import Form


class StockLocationCreateWizard(models.TransientModel):
    _name = "stock.location.create.wizard"

    name = fields.Char(string="Nombre", required=True)
    scrap_location = fields.Boolean(string="¿Es una ubicación de chatarra?", default=False)
    return_location = fields.Boolean(string="¿Es una ubicación de devolución?", default=False)
    location_id = fields.Many2one("stock.location", string="Ubicación padre")
    account_analytic_account_id = fields.Many2one("account.analytic.account", string="Cuenta Analitica")

    def action_create_stock_location(self):
        record = self.env["stock.location"]
        location = Form(record)
        location.name = self.name
        location.scrap_location = self.scrap_location
        location.return_location = self.return_location
        location.location_id = self.location_id
        location.save()
        self.account_analytic_account_id.stock_location_id = location.id
        return location 
