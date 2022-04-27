from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = "hr.contract"

    nominal_position_id = fields.Many2one("hr.nominal.position", string="Cargo Nominal")

    @api.model
    def create(self, vals):
        res = super().create(vals)
        register_salary_change(self, res, vals)
        return res

    def write(self, vals):
        res = super().write(vals)
        contract = self.env["hr.contract"].search([("id", '=', self.id)])
        register_salary_change(self, contract, vals)
        return res


def register_salary_change(self, contract, vals):
    salary_changed = False
    keys = ("wage", "wage_type", "hourly_wage")
    for key in keys:
        if key in vals:
            salary_changed = True
            break;
    if salary_changed:
        self.env["hr.employee.salary.change"].sudo().create({
            "contract_id": contract.id,
            "wage_type": contract.wage_type,
            "wage": contract.wage,
            "hourly_wage": contract.hourly_wage,
        })
