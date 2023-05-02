{
    "name": "Clickup Payload Import",
    "version": "14.0.1.0.0",
    "website": "https://github.com/OCA/server-tools",
    "author": "Odoo Community Association (OCA)",
    "category": "Clickup Payload Import/management",
    "summary": "clickup payload import",
    "depends": [
        "project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/project_inherited_view.xml",
        "wizard/import_clickup_wizard_view.xml",
        "views/import_clickup_menu_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
