from odoo import fields, models


class HrAllowance(models.Model):
    _name = "hr.allowance"
    _description = "Complementos salariales"

    name = fields.Char(string="Nombre", required=True)
    active = fields.Boolean(default=True)
    value = fields.Float(string="Valor", required=True)
    description = fields.Text(string="Descripción", required=True)
    state = fields.Selection(
        selection=[("active", "Activo"), ("inactive", "Inactivo")],
        default="active", string="Estatus")
