{
    "name": "Yacambu Account",
    "version": "1.0.1",
    "author": "Binaural",
    "support": "contacto@binauraldev.com",
    "description": """""",
    "depends": [
        "account",
        "account_accountant",
        "account_asset",
        "approvals",
        "binaural_contactos_configuraciones",
        "contacts",
        "purchase",
    ],
    "data": [
        "views/approval.xml",
        "views/partner_files.xml",
        "views/purchase.xml",
        "views/res_partner.xml",
        "views/menuitems.xml",
        "views/account_asset.xml",
        "report/yacambu_account_payment_templates.xml",
        "security/ir.model.access.csv",
    ],
    "images": ["static/description/icon.png"],
    "installable": True,
    "auto_install": False,
}
