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
    egress_date = fields.Date(string="Fecha de egreso", tracking=True)
    seniority = fields.Char(string="Antigüedad", compute="_compute_seniority")

    dependant_ids = fields.One2many("hr.employee.dependant", "employee_id", string="Dependientes", store=True)
    degree_ids = fields.One2many("hr.employee.degree", "employee_id", string="Estudios Realizados", store=True)
    bank_ids = fields.One2many("hr.employee.bank", "employee_id", string="Información Bancaria")

    @api.depends("entry_date", "egress_date")
    def _compute_seniority(self):
        for employee in self:
            seniority = ""
            if employee.entry_date:
                from_date = employee.entry_date
                to_date = employee.egress_date if employee.egress_date else fields.Date.today()

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

    @api.constrains("entry_date", "egress_date")
    def _check_dates(self):
        for employee in self:
            if employee.egress_date and employee.egress_date <= employee.entry_date:
                raise ValidationError(_("La fecha de egreso debe ser mayor a la fecha de ingreso"))
