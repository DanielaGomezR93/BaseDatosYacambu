{
    "name": "Yacambu Nomina",
    "version": "1.0.1",
    "author": "Binaural",
    "support": "contacto@binauraldev.com",
    "description": """
        Modulo que contiene modificaciones para la implementacion de nomina
        de yacambu ERP.
    """,
    "depends": [
        "base",
        "binaural_contactos_configuraciones",
        "hr",
        "hr_payroll",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_employee.xml",
        "views/hr_headquarter.xml",
        "views/hr_nominal_position.xml",
        "views/menuitems.xml",
    ],
    "images": ["static/description/icon.png"],
    "installable": True,
    "auto_install": False,
}
