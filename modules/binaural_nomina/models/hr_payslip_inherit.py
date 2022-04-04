from odoo import api, fields, models, _
from odoo.addons.binaural_nomina.models.browsable_object_inherit import IvssVzla

import logging
_logger = logging.getLogger(__name__)

class BinauralHrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'
    _description = 'Herencia pay slip de odoo para personalizaciones Venezuela'

    # def _get_localdict(self):
    #     _logger.info('AQUI AQUI')
    #     result = super(BinauralHrPayslipInherit, self)._get_localdict()
    #     result.update({
    #         'ivss': 
    #     })
    #     return result

    def _get_base_local_dict(self):
        variable = IvssVzla(self.env['ir.config_parameter'].sudo().get_param('porcentaje_deduccion_ivss'))
        _logger.info('LA VARIABLE %s', variable.porc_ivss)
        return {
            'porc_ivss': IvssVzla(self.env['ir.config_parameter'].sudo().get_param('porcentaje_deduccion_ivss')).porc_ivss
        }
