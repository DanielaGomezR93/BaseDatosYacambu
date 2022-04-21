from odoo import fields, models


class HrNominalPosition(models.Model):
    _name = "hr.nominal.position"
    _description = "Cargo Nominal"

    name = fields.Char(string="Descripción", required=True)
    active = fields.Boolean(default=True)
    contract_ids = fields.One2many(
        "hr.contract", "nominal_position_id", string="Contratos")

    _sql_constraints = [
        ("unique_name", "UNIQUE(name)",
         "Este cargo nominal ya existe"),
    ]
