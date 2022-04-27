# -*- coding: utf-8 -*-
{
    'name': "binaural_nomina",

    'summary': """
        Personalizaciones para la nomina de Venezuela
        """,

    'description': """
        Modulo que agrega las personalizaciones de ley para Venezuela, incluye FAOV, INCE, IVSS, Paro Forzoso
    """,

    'author': "Binaural C.A.",
    'website': "https://binauraldev.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','hr_holidays','hr_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_binaural.xml',        
        'views/hr_payslip_binaural.xml',
        'views/views.xml',
        'views/templates.xml',               
        'views/hr_menu_binaural.xml',        
        'views/res_config.xml',        
        'data/master_data.xml',
        'data/rules_data.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
