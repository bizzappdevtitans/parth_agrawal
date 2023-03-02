# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    "name": "School_Management",
    "version": "1.1",
    "category": "School_Management/management",
    "summary": "school management System",
    "description": """
This module contains all the common features of School management system
    """,
    "depends": [
        "base",
        "mail",
        "sale",
        "stock",
        "account",
        "sale_project",
        "sale_purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/Details_view.xml",
        "views/option_view.xml",
        "views/Studycorner_view.xml",
        "views/subjects_view.xml",
        "views/createrecord_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
