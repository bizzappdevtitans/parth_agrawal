from odoo import fields, models


class sale_order_line(models.Model):
    """To create new custom field in sale order line"""
    _inherit = "sale.order.line"

    available = fields.Boolean(string="Available")
