from odoo import fields, models


class ProductInherited(models.Model):
    _inherit = "product.product"

    purchase_order_data = fields.One2many(
        "purchase.order.line", "product_id", string="purchase_order_line", limit=5
    )

    sale_order_data = fields.One2many(
        "sale.order.line", "product_id", string="sale_order_line", limit=5
    )
