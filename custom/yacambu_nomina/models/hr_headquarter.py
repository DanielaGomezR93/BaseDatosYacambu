from odoo import api, fields, models


class HrHeadquarter(models.Model):
    _name = "hr.headquarter"
    _description = "Sede Administrativa"

    name = fields.Char(string="Nombre", required=True)
    code = fields.Char(string="Código", required=True)
    active = fields.Boolean(default=True)
    street = fields.Char(string="Calle")
    street2 = fields.Char(string="Calle 2")
    city_id = fields.Many2one(
        "res.country.city", string="Ciudad", required=True, domain="[('state_id', '=', state_id)]")
    state_id = fields.Many2one(
        "res.country.state", string="Estado", required=True, domain="[('country_id', '=', country_id)]")
    zip = fields.Char(string="Código Postal", change_default=True)

    def default_country_id(self):
        return self.env.ref("base.ve")

    country_id = fields.Many2one(
        "res.country", string="País", default=default_country_id)

    _sql_constraints = [
        ("unique_name", "UNIQUE(name)",
         "Una sede administrativa con ese nombre ya existe"),
        ("unique_code", "UNIQUE(code)",
         "Una sede administrativa con ese código ya existe"),
    ]

    def name_get(self):
        result = []
        for headquarter in self:
            result.append((headquarter.id, "[%s]%s" % (headquarter.code, headquarter.name)))
        return result
