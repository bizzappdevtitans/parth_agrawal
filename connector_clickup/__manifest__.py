{
    "name": "Connector Clickup",
    "version": "14.0.1.0.0",
    "website": "https://github.com/OCA/server-tools",
    "author": "Odoo Community Association (OCA)",
    "category": "Connector Clickup/management",
    "summary": "Connector Clickup",
    "depends": [
        "project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/connector_clickup_backend_view.xml",
        "views/inherited_project_module_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
