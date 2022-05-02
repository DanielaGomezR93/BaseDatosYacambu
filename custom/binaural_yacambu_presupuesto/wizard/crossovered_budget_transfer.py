from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CrossoveredBudgetTransferWizard(models.TransientModel):
    _name = "crossovered.budget.transfer.wizard"
    
    name = fields.Char(string="Nro control", required=True)
    date = fields.Date(string="Fecha de solicitud", default=fields.Date.today(), required=True)
    currency_id = fields.Many2one("res.currency", related="origin_budget_id.currency_id")

    origin_budget_id = fields.Many2one(
        "crossovered.budget", string="Unidad Origen", domain="[('state', 'in', ('confirm', 'validate'))]", required=True)
    origin_budget_line_ids = fields.Many2many(
        "crossovered.budget.lines", compute="_compute_origin_line_ids", string="Líneas del Presupuesto de origen")
    transfer_line_ids = fields.Many2many(
        "crossovered.budget.transfer.line.wizard", relation="budget_transfer_wizard_budget_line_rel",
        compute="_compute_transfer_line_ids", string="Lineas de Transferencia", readonly=False)
    destination_budget_id = fields.Many2one(
        "crossovered.budget", string="Unidad Destino", required=True,
        domain="[('id', '!=', origin_budget_id), ('state', 'not in', ('cancel', 'done'))]")
    general_budget_id = fields.Many2one("account.budget.post", string="Situación Presupuestaria", required=True)

    origin_available_amount = fields.Monetary(
        string="Monto disponible de la Unidad Origen",
        related="origin_budget_id.available_amount")
    amount_to_be_transfered = fields.Monetary(string="Monto a transferir", compute="_compute_amount_to_be_transfered")
    destination_available_amount = fields.Monetary(
        string="Monto disponible de la Unidad Destino",
        related="destination_budget_id.available_amount")
    updated_amount = fields.Monetary(compute="_compute_updated_amount", string="Monto Actualizado")

    @api.depends("origin_budget_id")
    def _compute_origin_line_ids(self):
        for transfer in self:
            transfer.origin_budget_line_ids = []
            for line in transfer.origin_budget_id.crossovered_budget_line:
                transfer.origin_budget_line_ids += line

    @api.depends("origin_budget_line_ids")
    def _compute_transfer_line_ids(self):
        for transfer in self:
            lines = []
            for line in transfer.origin_budget_line_ids:
                lines += self.env["crossovered.budget.transfer.line.wizard"].create({
                    "crossovered_budget_lines_id": line.id
                })
            transfer.transfer_line_ids = [budget_line.id for budget_line in lines]

    @api.depends("transfer_line_ids")
    def _compute_amount_to_be_transfered(self):
        for transfer in self:
            if any(transfer.transfer_line_ids):
                transfer.amount_to_be_transfered = sum(transfer.transfer_line_ids.mapped("amount_to_be_transfered"))
            else:
                transfer.amount_to_be_transfered = 0

    @api.depends("amount_to_be_transfered", "destination_available_amount")
    def _compute_updated_amount(self):
        for transfer in self:
            transfer.updated_amount = transfer.amount_to_be_transfered + transfer.destination_available_amount

    @api.onchange("amount_to_be_transfered", "origin_budget_id")
    def insufficient_amount_on_a_single_line_of_the_origin(self):
        if self.origin_available_amount == 0:
            raise ValidationError(
                "Este presupuesto no tiene disponibilidad.")

    @api.constrains("transfer_line_ids")
    def check_amount_to_be_transfered(self):
        is_sufficient = False
        for line in self.transfer_line_ids:
            if line.available_amount >= line.amount_to_be_transfered:
                is_sufficient = True
                break
        if not is_sufficient:
            raise ValidationError(
                "No existe ninguna linea de la unidad origen que tenga disponible la cantidad a transferir.")

    def action_transfer_amount(self):
        record = self.env["crossovered.budget.transfer"]
        
        new_origin = self.env["crossovered.budget"].create({
            "name": self.origin_budget_id.name,
            "user_id": self.origin_budget_id.user_id.id,
            "date_from": self.origin_budget_id.date_from,
            "date_to": self.origin_budget_id.date_to,
        }) 
        new_lines = []

        is_transfered = False
        new_budget_lines = []
        for line in self.transfer_line_ids:
            params = {
                "crossovered_budget_id": new_origin.id,
                "general_budget_id": line.crossovered_budget_lines_id.general_budget_id.id,
                "analytic_account_id": line.crossovered_budget_lines_id.analytic_account_id.id,
                "date_from": line.crossovered_budget_lines_id.date_from,
                "date_to": line.crossovered_budget_lines_id.date_to,
                "paid_date": line.crossovered_budget_lines_id.paid_date,
                "planned_amount": line.planned_amount,
                "practical_amount": line.practical_amount,
                "theoritical_amount": line.crossovered_budget_lines_id.theoritical_amount,
            }
            if not is_transfered:
                if line.available_amount > 0 and line.available_amount > self.amount_to_be_transfered or\
                        line.available_amount < 0 and line.available_amount < self.amount_to_be_transfered:
                    params["planned_amount"] -= self.amount_to_be_transfered
                    is_transfered = True
            new_budget_lines += self.env["crossovered.budget.lines"].create(params)

            general_budget_id = line.destination_general_budget_id.id if\
                    line.destination_general_budget_id else line.origin_general_budget_id.id
            new_line_date_from = self.date
            if self.date < self.destination_budget_id.date_from or self.date > self.destination_budget_id.date_to:
                new_line_date_from = self.destination_budget_id.date_from
            new_lines += self.env["crossovered.budget.lines"].create({
                "crossovered_budget_id": self.destination_budget_id.id,
                "general_budget_id": general_budget_id,
                "analytic_account_id": line.analytic_account_id.id,
                "paid_date": line.crossovered_budget_lines_id.paid_date,
                "planned_amount": line.amount_to_be_transfered,
                "practical_amount": line.practical_amount,
                "theoritical_amount": line.crossovered_budget_lies_id.theoritical_amount,
                "date_from": new_line_date_from,
                "date_to": self.destination_budget_id.date_to,
            })

        self.origin_budget_id.write({
            "name": self.origin_budget_id.name + " (TRANSFERIDO)",
            "has_been_transfered": True,
        })
        self.origin_budget_id.action_budget_cancel()
        new_origin.action_budget_confirm()

        record.create({
            "name": self.name,
            "date": self.date,
            "user_id": self.env.uid,
            "cancelled_budget_id": self.origin_budget_id.id,
            "destination_budget_id": self.destination_budget_id.id,
            "new_origin_budget_id": new_origin.id,
            "destination_budget_new_line_ids": new_lines.mapped("id"),
            "general_budget_id": self.general_budget_id.id,
            "origin_available_amount": self.origin_available_amount,
            "amount_to_be_transfered": self.amount_to_be_transfered,
            "destination_available_amount": self.destination_available_amount,
            "updated_amount": self.updated_amount,
        })


class CrossoveredBudgetTransferLineWizard(models.TransientModel):
    _name = "crossovered.budget.transfer.line.wizard"

    crossovered_budget_lines_id = fields.Many2one(
        "crossovered.budget.lines", relation="budget_transfer_lines_wizard_rel",
        string="Lineas de presupuesto")
    currency_id = fields.Many2one(
        "res.currency", related="crossovered_budget_lines_id.currency_id")
    origin_general_budget_id = fields.Many2one(
        "account.budget.post", string="Posición presupuestaria origen",
        related="crossovered_budget_lines_id.general_budget_id")
    destination_general_budget_id = fields.Many2one(
        "account.budget.post", string="Posición presupuestaria destino")
    analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Cuenta analítica",
        related="crossovered_budget_lines_id.analytic_account_id")
    planned_amount = fields.Monetary(
        string="Importe previsto", related="crossovered_budget_lines_id.planned_amount")
    practical_amount = fields.Monetary(
        string="Importe real", related="crossovered_budget_lines_id.practical_amount")
    available_amount = fields.Monetary(
        string="Disponible", related="crossovered_budget_lines_id.available_amount")
    amount_to_be_transfered = fields.Monetary(string="Cantidad a Transferir")

