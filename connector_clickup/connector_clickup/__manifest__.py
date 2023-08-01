{
    "name": "ClickUp Connector",
    "version": "16.0.1.0.0",
    "category": "Connector",
    "depends": ["connector", "projects_task_checklists"],
    "author": "Bizzappdev",
    "license": "LGPL-3",
    "website": "https://bizzappdev.com",
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "data/queue_job_data.xml",
        "views/connector_clickup_backend_view.xml",
        "views/project_project_view.xml",
        "views/project_task_type_view.xml",
        "views/project_task_view.xml",
        "views/task_checklist_view.xml",
        "views/res_company_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
