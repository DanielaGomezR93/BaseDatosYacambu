from . import fields, models
from odoo.tests.common import Form


class CrossoveredBudgetTransferWizard(models.TransientModel):
    _name = "crossovered.budget.transfer.wizard"
    
    name = fields.Char(string="Nro control")
    date = fields.Date(string="Fecha de solicitud")

    origin_budget_id = fields.Many2one("crossovered.budget", string="Unidad Origen")
    destination_budget_id = fields.Many2one("crossovered.budget", string="Unidad Destino")

    origin_available_amount = fields.Monetary(
        string="Monto disponible de la Unidad Origen",
        related="origin_budget_id.available_amount")
    amount_to_be_transfered = fields.Monetary(string="Monto a transferir")
    destination_available_amount = fields.Monetary(
        string="Monto disponible de la Unidad Destino",
        related="destination_budget_id.available_amount")
    updated_amount = fields.Monetary(
        compute=lambda t: t.amount_to_be_transfered + t.destination_available_amount,
        string="Monto Actualizado")

    def action_transfer_amount(self):
        record = self.env["crossovered.budget.transfer"]
        transfer = Form(record)
        transfer.cancelled_budget_id = self.origin_budget_id
        transfer.destination_budget_id = self.destination_budget_id

        #TODO Modelo de transferencia de presupuestos con sus campos definidos para la logica de este metodo

        new_origin = self.origin_budget_id.copy()
        new_line = "Aqui debe definirse la nueva line de presupuesto" #TODO
        transfer.new_origin = new_origin
        transfer.destination_budget_new_line_id = new_line
