from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class BinauralHrContractInherit(models.Model):
    _inherit = 'hr.contract'
    _description = 'Herencia contrato para Venezuela'

    