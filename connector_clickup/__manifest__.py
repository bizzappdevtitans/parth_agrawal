{
    "name": "ClickUp Connector",
    "version": "16.0.1.0.0",
    "category": "Connector",
    "depends": [
        "project",
        "connector",
        "queue_job",
    ],
    "author": "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "website": "https://bizzappdev.com",
    "images": [],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "data/queue_job_data.xml",
        "views/connector_clickup_backend_view.xml",
        "views/inherited_project_module_view.xml",
    ],
    "installable": True,
    "application": True,
}
