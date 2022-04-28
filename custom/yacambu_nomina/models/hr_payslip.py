from odoo import models
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject
import logging
_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def _get_base_local_dict(self):
        local_dict = super()._get_base_local_dict()

        allowances = self.employee_id.mapped("allowance_line_ids")
        allowances_dict = {allowance.code: allowance.value for allowance in allowances}

        employee = self.employee_id

        _logger.warning(BrowsableObject(employee.id, allowances_dict, self.env))

        local_dict.update({
            "allowances": BrowsableObject(employee.id, allowances_dict, self.env)
        })

        return local_dict
