from odoo import api, fields, models


class HrDepartment(models.Model):
    _inherit = "hr.department"

    code = fields.Char(string="Código")
    
    def name_get(self):
        result = []
        for department in self:
            if department.code:
                result.append((department.id, "[%s]%s" % (department.code, department.name)))
            else:
                result.append((department.id, "%s" % (department.name)))
        return result
