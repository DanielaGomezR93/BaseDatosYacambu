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
        "base", "binaural_contactos_configuraciones", "hr",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_headquarter.xml",
        "views/menuitems.xml",
    ],
    "images": ["static/description/icon.png"],
    "installable": True,
    "auto_install": False,
}
