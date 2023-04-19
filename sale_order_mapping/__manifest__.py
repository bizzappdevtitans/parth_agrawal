# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    "name": "Sale Order Mapping",
    "version": "14.0.1.0.0",
    "category": "Sale order Mapping/management",
    "summary": "sale order mapping",
    "website": "https://github.com/OCA/server-tools",
    "author": "Odoo Community Association (OCA)",
    "depends": [
        "sale",
        "stock",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/create_data_view.xml",
        "views/create_record_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
