{
    "name": "Binaural Nomina",
    "version": "1.0.1",
    "author": "Binaural",
    "support": "contacto@binauraldev.com",
    "description": """
        Modulo que contiene modificaciones para la implementacion de nomina
        de yacambu ERP.
    """,
    "depends": [
        "base", "hr",
    ],
    "data": [
        "views/hr_headquarter.xml",
        "views/menuitems.xml",
        "security/ir.model.access",
    ],
    "images": ["static/description/icon.png"],
    "installable": True,
    "auto_install": False,
}
