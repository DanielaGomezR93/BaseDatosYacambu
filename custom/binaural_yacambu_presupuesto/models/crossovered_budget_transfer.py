from odoo import fields, models


class CrossoveredBudgetTransfer(models.Model):
    _name = "crossovered.budget.transfer"
    _description = "Transferencias de Presupuesto"

    name = fields.Char(string="Nro control")
    date = fields.Date(string="Fecha de solicitud", readonly=True)
    user_id = fields.Many2one(
        "res.users", string="Usuario", help="Quien realizó la transferencia.", readonly=True)
    line_ids = fields.One2many(
        "crossovered.budget.transfer.line", "transfer_id",
        string="Líneas de transferencia de presupuesto", readonly=True, required=True)
    currency_id = fields.Many2one(
        "res.currency", related="cancelled_budget_id.currency_id", store=True)
    cancelled_budget_id = fields.Many2one(
        "crossovered.budget", string="Unidad Origen (Cancelada)", readonly=True)
    new_origin_budget_id = fields.Many2one(
        "crossovered.budget", string="Unidad Origen (Generada en la transferencia)", readonly=True)
    destination_budget_id = fields.Many2one(
        "crossovered.budget", string="Unidad Destino", readonly=True)
    origin_available_amount = fields.Monetary(
        string="Monto disponible de la Unidad Origen", readonly=True)
    amount_to_be_transfered = fields.Monetary(
        string="Monto a transferir", readonly=True)
    destination_available_amount = fields.Monetary(
        string="Monto disponible de la Unidad Destino", readonly=True)
    updated_amount = fields.Monetary(string="Monto Actualizado", readonly=True)


class CrossoveredBudgetTransferLine(models.Model):
    _name = "crossovered.budget.transfer.line"
    _description = "Lineas de Transferencias de Presupuesto"

    transfer_id = fields.Many2one(
        "crossovered.budget.transfer", string="Transferencia",
        required=True, readonly=True)
    origin_analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Cuenta origen",
        required=True, readonly=True)
    destination_analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Cuenta destino",
        required=True, readonly=True)
    currency_id = fields.Many2one(
        "res.currency", related="transfer_id.currency_id", store=True)
    transfered_amount = fields.Monetary(
        string="Monto transferido", required=True, readonly=True)
    origin_general_budget_id = fields.Many2one(
        "account.budget.post", string="Posición presupuestaria origen",
        required=True, readonly=True)
    destination_general_budget_id = fields.Many2one(
        "account.budget.post", string="Posición presupuestaria destino",
        required=True, readonly=True)
