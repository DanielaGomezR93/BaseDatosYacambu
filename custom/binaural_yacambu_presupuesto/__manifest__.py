{
    "name": "Binaural Yacambu Presupuesto",
    "version": "1.0.1",
    "author": "Binaural",
    "support": "contacto@binauraldev.com",
    "description": """
        Modulo que contiene las modificaciones de presupuesto de Yacambu ERP.
    """,
    "depends": [
        "account_budget",
        "yacambu_account",
    ],
    "data": [
        "views/account_analytic.xml",
        "views/account_budget.xml",
    ],
    "images": ["static/description/icon.png"],
    "installable": True,
    "auto_install": False,
}
