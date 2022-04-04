# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class ResConfigSettingsBinauralNomina(models.TransientModel):
    _inherit = 'res.config.settings'

    sueldo_base_ley = fields.Float(string="Sueldo base de ley", help="Sueldo base de ley", digits=(9,2))
    porcentaje_deduccion_faov = fields.Float(string="Porcentaje de deduccion FAOV", help="Porcentaje que se usara para la deduccion", digits=(5,2))
    porcentaje_deduccion_ince = fields.Float(string="Porcentaje de deduccion INCE", help="Porcentaje que se usara para la deduccion", digits=(5,2))        

    porcentaje_deduccion_ivss = fields.Float(string="Porcentaje de deduccion IVSS", help="Porcentaje que se usara para la deduccion", digits=(5,2))
    tope_salario_ivss = fields.Integer(string="Tope salario IVSS", help="Cantidad de salarios maximos usados para el calculo de la deduccion")
    monto_maximo_ivss = fields.Float(string="Monto maximo deduccion", store=True, readonly=True)

    porcentaje_deduccion_pf = fields.Float(string="Porcentaje de deduccion Paro Forzoso", help="Porcentaje que se usara para la deduccion", digits=(5,2))
    tope_salario_pf = fields.Integer(string="Tope salario Paro Forzoso", help="Cantidad de salarios maximos usados para el calculo de la deduccion")
    monto_maximo_pf = fields.Float(string="Monto maximo deduccion Paro Forzoso", store=True, readonly=True)

    def set_values(self):
        super(ResConfigSettingsBinauralNomina, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('sueldo_base_ley',self.sueldo_base_ley)

        self.env['ir.config_parameter'].sudo().set_param('porcentaje_deduccion_faov',self.porcentaje_deduccion_faov)
        self.env['ir.config_parameter'].sudo().set_param('porcentaje_deduccion_ince',self.porcentaje_deduccion_ince)

        self.env['ir.config_parameter'].sudo().set_param('porcentaje_deduccion_ivss',self.porcentaje_deduccion_ivss)
        self.env['ir.config_parameter'].sudo().set_param('tope_salario_ivss',self.tope_salario_ivss)
        self.env['ir.config_parameter'].sudo().set_param('monto_maximo_ivss',self.monto_maximo_ivss)

        self.env['ir.config_parameter'].sudo().set_param('porcentaje_deduccion_pf',self.porcentaje_deduccion_pf)
        self.env['ir.config_parameter'].sudo().set_param('tope_salario_pf',self.tope_salario_pf)
        self.env['ir.config_parameter'].sudo().set_param('monto_maximo_pf',self.monto_maximo_pf)
        

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsBinauralNomina, self).get_values()
        res['sueldo_base_ley'] = self.env['ir.config_parameter'].sudo().get_param('sueldo_base_ley')

        res['porcentaje_deduccion_faov'] = self.env['ir.config_parameter'].sudo().get_param('porcentaje_deduccion_faov')
        res['porcentaje_deduccion_ince'] = self.env['ir.config_parameter'].sudo().get_param('porcentaje_deduccion_ince')
        
        res['porcentaje_deduccion_ivss'] = self.env['ir.config_parameter'].sudo().get_param('porcentaje_deduccion_ivss')
        res['tope_salario_ivss'] = self.env['ir.config_parameter'].sudo().get_param('tope_salario_ivss')
        res['monto_maximo_ivss'] = self.env['ir.config_parameter'].sudo().get_param('monto_maximo_ivss')

        res['porcentaje_deduccion_pf'] = self.env['ir.config_parameter'].sudo().get_param('porcentaje_deduccion_pf')
        res['tope_salario_pf'] = self.env['ir.config_parameter'].sudo().get_param('tope_salario_pf')
        res['monto_maximo_pf'] = self.env['ir.config_parameter'].sudo().get_param('monto_maximo_pf')
        return res

    @api.onchange('sueldo_base_ley','tope_salario_ivss','tope_salario_pf')
    def _onchange_topes_maximos(self):
        self.monto_maximo_ivss = self.sueldo_base_ley * self.tope_salario_ivss
        self.monto_maximo_pf = self.sueldo_base_ley * self.tope_salario_pf

        