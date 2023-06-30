{
    "name": "ClickUp Connector",
    "version": "16.0.1.0.0",
    "category": "Connector",
    "depends": [
        "project",
        "connector",
    ],
    "author": "Bizzappdev",
    "license": "LGPL-3",
    "website": "https://bizzappdev.com",
    "images": [],
    "qweb": [
        "static/src/xml/custom.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "connector_clickup/static/src/js/custom.js",
        ],
    },
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "data/queue_job_data.xml",
        "views/connector_clickup_backend_view.xml",
        "views/inherited_project_module_view.xml",
        "views/res_company_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "installable": True,
    "application": False,
}
