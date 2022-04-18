from datetime import datetime
from dateutil import relativedelta
from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    headquarter_id = fields.Many2one("hr.headquarter", string="Sede Administrativa")
    entry_date = fields.Date(string="Fecha de ingreso", required=True)
    egress_date = fields.Date(string="Fecha de egreso")
    seniority = fields.Char(string="Antigüedad", compute="_compute_seniority")

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
