from datetime import datetime
from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    headquarter_id = fields.Many2one("hr.headquarter", string="Sede Administrativa", tracking=True)
    allowance_line_ids = fields.One2many("hr.allowance.line", "employee_id", string="Complementos Salariales", tracking=True)
