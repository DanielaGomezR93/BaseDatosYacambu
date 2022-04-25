from odoo import fields, models


class CrossoveredBudgetTransfer(models.Model):
    _name = "crossovered.budget.transfer"
    _description = "Lleva registro de las transferencias entre presupuestos."

    name = fields.Char(string="Nro control")
    date = fields.Date(string="Fecha de solicitud", readonly=True)
    general_budget_id = fields.Many2one("account.budget.post", string="Situación Presupuestaria", readonly=True)
    currency_id = fields.Many2one("res.currency", related="cancelled_budget_id.currency_id")
    cancelled_budget_id = fields.Many2one("crossovered.budget", string="Unidad Origen (Cancelada)", readonly=True)
    new_origin_budget_id = fields.Many2one(
        "crossovered.budget", string="Unidad Origen (Generada en la transferencia)", readonly=True)
    destination_budget_id = fields.Many2one("crossovered.budget", string="Unidad Destino", readonly=True)
    destination_budget_new_line_id = fields.Many2one("crossovered.budget.lines", string="Linea de presupuesto")
    origin_available_amount = fields.Monetary(string="Monto disponible de la Unidad Origen", readonly=True)
    amount_to_be_transfered = fields.Monetary(string="Monto a transferir", readonly=True)
    destination_available_amount = fields.Monetary(string="Monto disponible de la Unidad Destino", readonly=True)
    updated_amount = fields.Monetary(string="Monto Actualizado", readonly=True)
