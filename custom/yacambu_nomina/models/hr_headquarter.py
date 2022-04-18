from odoo import api, fields, models


class HrHeadquarter(models.Model):
    _name = "hr.headquarter"
    _description = "Sede Administrativa"

    name = fields.Char(string="Nombre")
    active = fields.Boolean()
    address = fields.Char(string="Dirección")
    city_id = fields.Many2one("res.country.city", string="Ciudad")
    state_id = fields.Many2one("res.country.state", string="Estado")

    _sql_constraints = [
        ("unique_name", "UNIQUE(name)",
         "Esta sede administrativa ya existe"),
    ]
