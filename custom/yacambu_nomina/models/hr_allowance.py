from odoo import api, fields, models


class HrAllowance(models.Model):
    _name = "hr.allowance"
    _description = "Complementos salariales"

    name = fields.Char(string="Nombre", required=True)
    code = fields.Char(string="Código", required=True)
    active = fields.Boolean(default=True)
    value = fields.Float(string="Valor", required=True)
    description = fields.Char(string="Descripción", required=True)


class HrAllowanceLine(models.Model):
    _name = "hr.allowance.line"
    _description = "Líneas de Complementos salariales"

    employee_id = fields.Many2one("hr.employee", string="Empleado")
    allowance_id = fields.Many2one("hr.allowance", string="Complemento")
    code = fields.Char(string="Código", related="allowance_id.code", store=True)
    value = fields.Float(string="Valor", compute="_compute_value", readonly=False, store=True)
    description = fields.Char(string="Descripción", related="allowance_id.description")


    @api.depends("allowance_id")
    def _compute_value(self):
        for line in self:
            line.value = line.allowance_id.value
