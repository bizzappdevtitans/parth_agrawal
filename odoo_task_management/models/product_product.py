from odoo import fields, models


class ProductInherited(models.Model):
    _inherit = "product.product"

    purchase_order_data = fields.One2many(
        "purchase.order.line",
        "product_id",
        string="purchase_order_line",
        limit=5,
        domain=[("state", "=", "purchase")],
    )

    sale_order_data = fields.One2many(
        "sale.order.line",
        "product_id",
        string="sale_order_line",
        domain=[("state", "=", "sale")],
        limit=5,
    )

    attachment_data = fields.Many2many(
        "ir.attachment", compute="_compute_attachments_product"
    )

    def _compute_attachments_product(self):
        product_attachment_count = self.env["ir.attachment"].search(
            [("res_model", "=", self._name), ("res_id", "=", self.id)]
        )
        self.attachment_data = product_attachment_count.ids

    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'product.product')])
