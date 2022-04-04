from odoo import fields
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject

import logging
_logger = logging.getLogger(__name__)

class IvssVzla(BrowsableObject):
    def __init__(self, porc_ivss):        
        self.porc_ivss = porc_ivss        

    def  __getattr__(self, attr):        
        return self.porc_ivss if self.porc_ivss else 0.0
    
        