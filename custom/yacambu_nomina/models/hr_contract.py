from odoo import fields, models, _


class HrContract(models.Model):
    _inherit = "hr.contract"

    nominal_position_id = fields.Many2one("hr.nominal.position", string="Cargo Nominal")
