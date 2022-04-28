from odoo import fields, models, _


class HrPayrollStructure(models.Model):
    _inherit = "hr.payroll.structure"

    schedule_pay = fields.Selection(selection_add=[("three-week", "Trisemanal")])

class HrPayrollStructureType(models.Model):
    _inherit = "hr.payroll.structure.type"

    default_schedule_pay = fields.Selection(selection_add=[("three-week", "Trisemanal")])
