from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class BinauralHrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'
    _description = 'Herencia empleado de odoo para personalizaciones nomina Venezuela'

    porc_ari = fields.Float(string="Porcentaje ARI", help="Porcentaje retencion ISLR", digits=(5,2), default=0.0)

    entry_date = fields.Date(string="Fecha de ingreso", required=True, tracking=True)
    seniority = fields.Char(string="Antigüedad", compute="_compute_seniority")

    dependant_ids = fields.One2many("hr.employee.dependant", "employee_id", string="Dependientes", store=True)
    degree_ids = fields.One2many("hr.employee.degree", "employee_id", string="Estudios Realizados", store=True)
    bank_ids = fields.One2many("hr.employee.bank", "employee_id", string="Información Bancaria")

    prefix_vat = fields.Selection([
        ('V', 'V'), ('E', 'E'),
    ], "Prefijo Rif", default='V')
    street = fields.Char(string="Calle")
    street2 = fields.Char(string="Calle 2")
    city_id = fields.Many2one(
        "res.country.city", "Ciudad", tracking=True, domain="[('state_id','=',state_id)]")
    state_id = fields.Many2one(
        "res.country.state", "Estado", tracking=True, domain="[('country_id','=',country_id)]")
    zip = fields.Char(string="Código Postal", change_default=True)
    municipality_id = fields.Many2one(
        'res.country.municipality', "Municipio", tracking=True, domain="[('state_id','=',state_id)]")
    house_type = fields.Selection([
        ("owned", "Propia"),
        ("rented", "Alquilada"),
        ("family", "Familiar"),
    ], "Vivienda", default="owned", tracking=True)
    private_mobile_phone = fields.Char(string="Teléfono celular personal", tracking=True)

    has_open_contract = fields.Boolean(string="Tiene Contrato", compute="_compute_has_open_contract")

    def default_country_id(self):
        return self.env.ref("base.ve")

    country_id = fields.Many2one(default=default_country_id)

    @api.depends("entry_date", "departure_date")
    def _compute_seniority(self):
        for employee in self:
            seniority = ""
            if employee.entry_date:
                from_date = employee.entry_date
                to_date = employee.departure_date if employee.departure_date else fields.Date.today()

                diff = relativedelta.relativedelta(to_date, from_date)

                years = diff.years
                months = diff.months
                days = diff.days

                years_string = "Años" if years > 1 else "Año"
                months_string = "Meses" if months > 1 else "Mes"
                days_string = "Días" if days > 1 else "Día"

                if days > 0:
                    seniority += f"{days} {days_string}"
                if months > 0 and days > 0:
                    seniority = f"{months} {months_string} / " + seniority
                elif months > 0:
                    seniority = f"{months} {months_string} " + seniority
                if years > 0 and (days > 0 or months > 0):
                    seniority = f"{years} {years_string} / " + seniority
                elif years > 0:
                    seniority = f"{years} {years_string} " + seniority
            employee.seniority = seniority

    @api.depends("contract_ids")
    def _compute_has_open_contract(self):
        for employee in self:
            employee.has_open_contract = False
            if any(self.env["hr.contract"].search([("state", '=', "open"), ("employee_id", '=', employee.id)])):
                employee.has_open_contract = True

    @api.constrains("entry_date", "departure_date")
    def _check_dates(self):
        for employee in self:
            if employee.departure_date and employee.departure_date <= employee.entry_date:
                raise ValidationError(_("La fecha de egreso debe ser mayor a la fecha de ingreso."))

    @api.constrains("identification_id", "prefix_vat")
    def _check_identification_id(self):
        for employee in self:
            employee_with_the_same_vat = self.env["hr.employee"].sudo().search([
                ("identification_id", '=', employee.identification_id),
                ("prefix_vat", '=', employee.prefix_vat),
                ("id", "!=", employee.id),
            ])
            if any(employee_with_the_same_vat):
                _logger.warning(self.env["hr.employee"].sudo().search([("identification_id",'=',employee.identification_id)]))
                raise ValidationError(_("Ya existe un empleado con ese RIF."))
