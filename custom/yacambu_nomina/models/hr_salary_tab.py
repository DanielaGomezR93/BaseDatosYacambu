from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tests.common import Form


class HrSalaryTab(models.Model):
    _name = "hr.salary.tab"
    _inherit = ["mail.thread"]
    _description = "Tabulador Salarial"

    name = fields.Char(string="Nombre", related="nominal_position_id.name")
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ("active", "Vigente"),
        ("inactive", "Inactivo"),
    ], string="Estatus", compute="_compute_state")
    date_from = fields.Date(
        string="Vigente desde", required=True, tracking=True)
    nominal_position_id = fields.Many2one(
        "hr.nominal.position", string="Cargo nominal", required=True, tracking=True)
    wage_type = fields.Selection(
        selection=[("monthly", "Salario Fijo Mensual"), ("hourly", "Salario por Hora")],
        string="Tipo de salario", required=True, tracking=True)
    wage = fields.Float(string="Salario Mensual", required=True, tracking=True)
    hourly_wage = fields.Float(string="Salario por Hora", tracking=True)
    food_allowance = fields.Float(string="Cestaticket", tracking=True)
    allowance = fields.Float(string="Complemento", tracking=True)
    aid = fields.Float(string="Ayuda", tracking=True)

    def action_update(self):
        for tab in self:
            if not tab.active:
                raise UserError(
                    _("No se pueden actualizar los salarios desde un tabulador inactivo."))
            contracts = self.env["hr.contract"].search([("nominal_position_id", '=', tab.nominal_position_id.id)])
            structure_types = contracts.mapped("structure_type_id")
            for structure_type in structure_types:
                with Form(structure_type) as s:
                    s.wage_type = tab.wage_type
            for contract in contracts:
                with Form(contract) as c:
                    if tab.wage_type == "monthly":
                        c.wage = tab.wage
                    if tab.wage_type == "hourly":
                        c.hourly_wage = tab.hourly_wage
            tab.message_post(body="Salarios Actualizados.")

    @api.depends("active")
    def _compute_state(self):
        for tab in self:
            tab.state = "active" if tab.active else "inactive"
