from odoo import fields, models, _


class ResConfig(models.TransientModel):
    _inherit = "res.config.settings"

    night_voucher_percentage = fields.Float(
        string="Porcentaje de calculo de Bono Nocturno", help="Porcentaje de calculo que se usará para el pago del Bono Nocturno")

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param('night_voucher_percentage',self.night_voucher_percentage)
