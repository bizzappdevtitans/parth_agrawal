# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    "name": "odoo_task_management",
    "version": "15.0.1.0.0",
    "category": "odoo_task_management/management",
    "summary": "odoo task management",
    "description": """
    This module contains all the common functionality added in odoo addons
    """,
    "depends": [
        "mail",
        "sale",
        "account",
        "project",
        "sale_project",
        "project",
        "purchase",
        "stock",
        "mrp",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/mail_compose_message_view.xml",
        "views/create_record_view.xml",
        "report/invoices_report.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
