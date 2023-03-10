from odoo import fields, models


class PurchaseOrderInherit(models.Model):
    """To pass value from SO to PO"""
    _inherit = "purchase.order"

    purchase_des = fields.Char(string="description")
