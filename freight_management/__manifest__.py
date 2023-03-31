# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'freight_management',
    'version': '15.0.1.0.0',
    "category": "freight_management/management",
    'summary': 'Module for Managing All Frieght Operations',
    'description': 'Module for Managing All Frieght Operations',
    'depends': ['base', 'product', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'security/group_security.xml',

        'data/freight_order_data.xml',
        'data/freight_revision_cron.xml',
        'data/freight_ir_server_actions.xml',

        'views/freight_order.xml',
        'views/freight_port.xml',
        'views/freight_container.xml',
        'views/freight_service_view.xml',
        'views/freight_price_view.xml',
        'views/freight_routes_view.xml',
        'views/freight_homepage_view.xml',
        'views/custom_clearance.xml',
        'views/order_track.xml',
        'views/action_menus.xml',
        'views/feedback_view.xml',

        'report/report_order.xml',
        'report/report_tracking.xml',

        'wizard/custom_revision.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
}
