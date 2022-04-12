from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CrossoveredBudgetTransferWizard(models.TransientModel):
    _name = "crossovered.budget.transfer.wizard"
    
    name = fields.Char(string="Nro control", required=True)
    date = fields.Date(string="Fecha de solicitud", default=fields.Date.today(), required=True)
    currency_id = fields.Many2one("res.currency", related="origin_budget_id.currency_id")

    origin_budget_id = fields.Many2one(
        "crossovered.budget", string="Unidad Origen", domain="[('state', 'in', ('confirm', 'validate'))]", required=True)
    destination_budget_id = fields.Many2one(
        "crossovered.budget", string="Unidad Destino", required=True,
        domain="[('id', '!=', origin_budget_id), ('state', 'not in', ('cancel', 'done'))]")

    origin_available_amount = fields.Monetary(
        string="Monto disponible de la Unidad Origen",
        related="origin_budget_id.available_amount")
    amount_to_be_transfered = fields.Monetary(string="Monto a transferir", required=True)
    destination_available_amount = fields.Monetary(
        string="Monto disponible de la Unidad Destino",
        related="destination_budget_id.available_amount")
    updated_amount = fields.Monetary(compute="_compute_updated_amount", string="Monto Actualizado")

    @api.depends("amount_to_be_transfered", "destination_available_amount")
    def _compute_updated_amount(self):
        for transfer in self:
            transfer.updated_amount = transfer.amount_to_be_transfered + transfer.destination_available_amount

    @api.onchange("amount_to_be_transfered", "origin_budget_id")
    def insufficient_amount_on_a_single_line_of_the_origin(self):
        if self.origin_available_amount == 0:
            raise ValidationError(
                "Este presupuesto no tiene disponibilidad.")

    @api.constrains("amount_to_be_transfered")
    def check_amount_to_be_transfered(self):
        if self.amount_to_be_transfered > self.origin_available_amount:
            raise ValidationError(
                "La unidad de origen no tiene disponible la cantidad a transferir.")
        for line in self.origin_budget_id.crossovered_budget_line:
            is_sufficient = False
            if line.available_amount > self.amount_to_be_transfered:
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

        is_transfered = False
        general_budget_id = None
        new_budget_lines = []
        for line in self.origin_budget_id.crossovered_budget_line:
            params = {
                "crossovered_budget_id": new_origin.id,
                "general_budget_id": line.general_budget_id.id,
                "analytic_account_id": line.analytic_account_id.id,
                "date_from": line.date_from,
                "date_to": line.date_to,
                "paid_date": line.paid_date,
                "planned_amount": line.planned_amount,
                "practical_amount": line.practical_amount,
                "theoritical_amount": line.theoritical_amount,
            }
            if not is_transfered:
                if line.available_amount > self.amount_to_be_transfered:
                    params["planned_amount"] -= self.amount_to_be_transfered
                    general_budget_id = params["general_budget_id"]
                    is_transfered = True
            new_budget_lines += self.env["crossovered.budget.lines"].create(params)
        if not general_budget_id:
            general_budget_id = new_budget_lines[0].general_budget_id

        self.origin_budget_id.write({
            "name": self.origin_budget_id.name + " (CANCELADO)",
            "has_been_transfered": True,
        })
        self.origin_budget_id.action_budget_cancel()
        new_origin.action_budget_confirm()

        new_line_date_from = self.date
        if self.date < self.destination_budget_id.date_from or self.date > self.destination_budget_id.date_to:
            new_line_date_from = self.destination_budget_id.date_from
        new_line = self.env["crossovered.budget.lines"].create({
            "crossovered_budget_id": self.destination_budget_id.id,
            "general_budget_id": general_budget_id,
            "date_from": new_line_date_from,
            "date_to": self.destination_budget_id.date_to,
            "planned_amount": self.amount_to_be_transfered,
        })

        record.create({
            "name": self.name,
            "date": self.date,
            "cancelled_budget_id": self.origin_budget_id.id,
            "destination_budget_id": self.destination_budget_id.id,
            "new_origin_budget_id": new_origin.id,
            "destination_budget_new_line_id": new_line.id,
            "origin_available_amount": self.origin_available_amount,
            "amount_to_be_transfered": self.amount_to_be_transfered,
            "destination_available_amount": self.destination_available_amount,
            "updated_amount": self.updated_amount,
        })
