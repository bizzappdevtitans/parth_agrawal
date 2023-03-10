# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    "name": "school_management",
    "version": "15.0.1.0.0",
    "category": "school_management/management",
    "summary": "School Management System",
    "description": """
This module contains all the common features of School Management System
    """,
    "depends": [
        "mail",
        "sale",
        "stock",
        "account",
        "sale_project",
        "sale_purchase",
        "mrp",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",

        "data/ir_sequence_data.xml",

        "wizard/create_data_view.xml",

        "views/details_view.xml",
        "views/option_view.xml",
        "views/studycorner_view.xml",
        "views/subjects_view.xml",
        "views/create_record_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
