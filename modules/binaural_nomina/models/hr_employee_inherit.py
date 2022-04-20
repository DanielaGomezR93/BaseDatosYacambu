from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class BinauralHrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'
    _description = 'Herencia empleado de odoo para personalizaciones nomina Venezuela'

    porc_ari = fields.Float(string="Porcentaje ARI", help="Porcentaje retencion ISLR", digits=(5,2), default=0.0)