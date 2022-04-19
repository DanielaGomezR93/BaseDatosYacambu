from datetime import  date
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class BinauralHrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'
    _description = 'Herencia pay slip de odoo para personalizaciones Venezuela'

    #Inherit functions
    def _get_base_local_dict(self):                
        local_dict_return = super(BinauralHrPayslipInherit, self)._get_base_local_dict()
        local_dict_return.update({
            'salario_minimo_actual': float(self.env['ir.config_parameter'].sudo().get_param('sueldo_base_ley')),
            'porc_faov': float(self.env['ir.config_parameter'].sudo().get_param('porcentaje_deduccion_faov')),
            'porc_ince': float(self.env['ir.config_parameter'].sudo().get_param('porcentaje_deduccion_ince')),
            'porc_ivss': float(self.env['ir.config_parameter'].sudo().get_param('porcentaje_deduccion_ivss')),
            'tope_ivss': float(self.env['ir.config_parameter'].sudo().get_param('tope_salario_ivss')),
            'maximo_deduccion_ivss': float(self.env['ir.config_parameter'].sudo().get_param('monto_maximo_ivss')),
            'porc_pf': float(self.env['ir.config_parameter'].sudo().get_param('porcentaje_deduccion_pf')),
            'tope_pf': float(self.env['ir.config_parameter'].sudo().get_param('tope_salario_pf')),
            'maximo_deduccion_pf': float(self.env['ir.config_parameter'].sudo().get_param('monto_maximo_pf'))
        })        
        return local_dict_return

    def _get_new_worked_days_lines(self):
        if self.struct_id.use_worked_day_lines:
            # computation of the salary worked days
            worked_days_line_values = self._get_worked_day_lines(check_out_of_contract=False)
            worked_days_lines = self.worked_days_line_ids.browse([])            
            for r in worked_days_line_values:
                r['payslip_id'] = self.id
                worked_days_lines |= worked_days_lines.new(r)                
            return worked_days_lines
        else:
            return [(5, False, False)]    

    def action_payslip_done(self):
        
        payslip_done_name = []
        message = ''
        for item in self:            
            payslips_done = self.env['hr.payslip'].search([
                ('date_from','=',self.date_from),
                # ('date_to','=',self.date_to),
                ('employee_id','=',item.employee_id.id),
                ('contract_id','=',item.contract_id.id),
                ('struct_id','=',item.struct_id.id),
                ('state','=','done')
            ])

            if payslips_done:
                payslip_done_name.append(item.number)                            

        if len(payslip_done_name) == 0:
            super(BinauralHrPayslipInherit, self).action_payslip_done()
        elif len(payslip_done_name) == 1:
            message = 'El recibo %s tiene las mismas caracteristicas (contrato y estructura), verifique la informacion e intente nuevamente' % (payslip_done_name[0])
            raise UserError(message)
        else:
            message = 'Los recibios %s tiene las mismas caracteristicas (contrato y estructura), verifique la informacion e intente nuevamente' % (", ".join(payslip_done_name))            
            raise UserError(message)
            


            
    # def compute_sheet(self):
    #     payslips = self.filtered(lambda slip: slip.state in ['draft', 'verify'])
    #     # delete old payslip lines
    #     payslips.line_ids.unlink()
    #     for payslip in payslips:
    #         number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
    #         lines = [(0, 0, line) for line in payslip._get_payslip_lines()]
    #         payslip.write({'line_ids': lines, 'number': number, 'state': 'verify', 'compute_date': fields.Date.today()})
    #     return True


    ## FUNCIONES PARA REGLAS
    def _compute_monday_in_range(self, id):        
        count = 0

        if id:    
            payslip = self.env['hr.payslip'].browse(id)

            date_from = date(payslip.date_from.year, payslip.date_from.month, payslip.date_from.day)
            date_to = date(payslip.date_to.year, payslip.date_to.month, payslip.date_to.day)            

            for d_ord in range(date_from.toordinal(), date_to.toordinal()+1):                
                d = date.fromordinal(d_ord)                                
                if (d.weekday() == 0):                    
                    count += 1
        else:
            raise UserWarning('Debe agregar un id de hr.payslip para el calculo de lunes')
                
        return count


