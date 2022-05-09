import logging
from odoo import api, fields, models
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class CrossoveredBudgetTransferWizard(models.Model):
    _name = "crossovered.budget.transfer.wizard"
    _description = "Wizard de Transferencias de presupuesto"
    
    name = fields.Char(string="Nro control", required=True)
    date = fields.Date(string="Fecha de solicitud", default=fields.Date.today(), required=True)
    currency_id = fields.Many2one("res.currency", related="origin_budget_id.currency_id")

    origin_budget_id = fields.Many2one(
        "crossovered.budget", string="Unidad Origen", domain="[('state', 'in', ('confirm', 'validate'))]", required=True, store=True)
    origin_budget_line_ids = fields.Many2many(
        "crossovered.budget.lines", compute="_compute_origin_line_ids",
        string="Líneas del Presupuesto de origen", store=True)
    transfer_line_ids = fields.One2many(
        "crossovered.budget.transfer.wizard.line", "transfer_wizard_ids",
        compute="_compute_transfer_line_ids", string="Lineas de Transferencia", readonly=False, store=True)
    destination_budget_id = fields.Many2one(
        "crossovered.budget", string="Unidad Destino", required=True, store=True,
        domain="[('id', '!=', origin_budget_id), ('state', 'not in', ('cancel', 'done'))]")

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
                lines += self.env["crossovered.budget.transfer.wizard.line"].create({
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

#     @api.constrains("transfer_line_ids")
#     def check_amount_to_be_transfered(self):
#         is_sufficient = False
#         for line in self.transfer_line_ids:
#             if line.available_amount > 0 and line.available_amount > self.amount_to_be_transfered or\
#                     line.available_amount < 0 and line.available_amount < self.amount_to_be_transfered:
#                 is_sufficient = True
#                 break
#         if not is_sufficient:
#             raise ValidationError(
#                 "No existe ninguna linea de la unidad origen que tenga disponible la cantidad a transferir.")

    def action_transfer_amount(self):
        record = self.env["crossovered.budget.transfer"]
        
        new_origin = self.env["crossovered.budget"].create({
            "name": self.origin_budget_id.name,
            "user_id": self.origin_budget_id.user_id.id,
            "date_from": self.origin_budget_id.date_from,
            "date_to": self.origin_budget_id.date_to,
        }) 

        new_budget_lines = []
        transfer_lines_params = []
        new_origin_budget_lines = []
        for line in self.transfer_line_ids:
            _logger.warning("Linea de Transferencia (Wizard)")
            _logger.warning(f"planned amount: {line.planned_amount}")
            _logger.warning(f"practical amount: {line.practical_amount}")
            _logger.warning(f"amount to be transfered: {line.amount_to_be_transfered}")
            is_transfered = False
            params = {
                "crossovered_budget_id": new_origin.id,
                "general_budget_id": line.origin_general_budget_id.id,
                "analytic_account_id": line.analytic_account_id.id,
                "date_from": self.origin_budget_id.date_from,
                "date_to": self.origin_budget_id.date_to,
                "paid_date": line.crossovered_budget_lines_id.paid_date,
                "planned_amount": line.planned_amount,
                "practical_amount": line.practical_amount,
                "theoritical_amount": line.crossovered_budget_lines_id.theoritical_amount,
            }
            _logger.warning("Date From of the new origin")
            _logger.warning(line.date_from)
            # if line.amount_to_be_transfered != 0:
                # if line.available_amount > 0 and line.available_amount > self.amount_to_be_transfered or\
                #         line.available_amount < 0 and line.available_amount < self.amount_to_be_transfered:
            params["planned_amount"] -= line.amount_to_be_transfered
            is_transfered = True
            if is_transfered:
                new_line_date_from = self.date
                if self.date < self.destination_budget_id.date_from or self.date > self.destination_budget_id.date_to:
                    new_line_date_from = self.destination_budget_id.date_from
                new_budget_lines += self.env["crossovered.budget.lines"].create({
                    "crossovered_budget_id": self.destination_budget_id.id,
                    "general_budget_id": line.destination_general_budget_id.id,
                    "analytic_account_id": line.analytic_account_id.id,
                    "paid_date": line.crossovered_budget_lines_id.paid_date,
                    "planned_amount": line.amount_to_be_transfered,
                    "practical_amount": line.practical_amount,
                    "theoritical_amount": line.crossovered_budget_lines_id.theoritical_amount,
                    "date_from": new_line_date_from,
                    "date_to": self.destination_budget_id.date_to,
                })
                _logger.warning("Budget Lines")
                _logger.warning(new_budget_lines)

                transfer_lines_params.append({
                    "analytic_account_id": line.analytic_account_id.id,
                    "transfered_amount": line.amount_to_be_transfered,
                    "origin_general_budget_id": line.origin_general_budget_id.id,
                    "destination_general_budget_id": line.destination_general_budget_id.id,
                })
            _logger.warning("Antes de crear la linea del nuevo presupuesto de origen")
            new_origin_budget_lines += self.env["crossovered.budget.lines"].create(params)
            _logger.warning("Despues de crear la linea del nuevo presupuesto de origen")

        self.origin_budget_id.write({
            "name": self.origin_budget_id.name + " (TRANSFERIDO)",
            "has_been_transfered": True,
        })
        self.origin_budget_id.action_budget_cancel()
        new_origin.action_budget_confirm()

        transfer = record.create({
            "name": self.name,
            "date": self.date,
            "user_id": self.env.uid,
            "cancelled_budget_id": self.origin_budget_id.id,
            "destination_budget_id": self.destination_budget_id.id,
            "new_origin_budget_id": new_origin.id,
            "line_ids": [],
            "origin_available_amount": self.origin_available_amount,
            "amount_to_be_transfered": self.amount_to_be_transfered,
            "destination_available_amount": self.destination_available_amount,
            "updated_amount": self.updated_amount,
        })
        _logger.warning("Transfer Line Params")
        _logger.warning(transfer_lines_params)

        for line_params in transfer_lines_params:
            line_params["transfer_id"] = transfer.id
            record.line_ids += self.env["crossovered.budget.transfer.line"].sudo().create(line_params)


class CrossoveredBudgetTransferLineWizard(models.Model):
    _name = "crossovered.budget.transfer.wizard.line"
    _description = "Lineas del wizard de transferencia de presupuesto"

    transfer_wizard_ids = fields.Many2one(
        "crossovered.budget.transfer.wizard",
        string="Wizard de Transferencia de Presupuesto", readonly=False, store=True)
    crossovered_budget_lines_id = fields.Many2one(
        "crossovered.budget.lines", string="Lineas de presupuesto", store=True)
    date_from = fields.Date(related="crossovered_budget_lines_id.date_from", store=True)
    date_to = fields.Date(related="crossovered_budget_lines_id.date_to", store=True)
    currency_id = fields.Many2one(
        "res.currency", related="crossovered_budget_lines_id.currency_id", store=True)
    origin_general_budget_id = fields.Many2one(
        "account.budget.post", string="Posición presupuestaria origen",
        related="crossovered_budget_lines_id.general_budget_id", store=True)
    destination_general_budget_id = fields.Many2one(
        "account.budget.post", string="Posición presupuestaria destino",
        compute="_compute_destination_general_budget_id", readonly=False, store=True)
    analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Cuenta analítica",
        related="crossovered_budget_lines_id.analytic_account_id", store=True)
    planned_amount = fields.Monetary(
        string="Importe previsto", related="crossovered_budget_lines_id.planned_amount", store=True)
    practical_amount = fields.Monetary(
        string="Importe real", related="crossovered_budget_lines_id.practical_amount", store=True)
    available_amount = fields.Monetary(
        string="Disponible", related="crossovered_budget_lines_id.available_amount", store=True)
    amount_to_be_transfered = fields.Float(string="Cantidad a Transferir", store=True)

    @api.depends("crossovered_budget_lines_id")
    def _compute_destination_general_budget_id(self):
        for line in self:
            line.destination_general_budget_id = line.crossovered_budget_lines_id.general_budget_id.id
