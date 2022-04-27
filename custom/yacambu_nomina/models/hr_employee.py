from datetime import datetime
from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    headquarter_id = fields.Many2one("hr.headquarter", string="Sede Administrativa", tracking=True)
