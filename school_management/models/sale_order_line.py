from odoo import fields, models


class sale_order_line(models.Model):
    """To create new custom field in sale order line"""

    _inherit = "sale.order.line"

    available = fields.Boolean(string="Available")
    product_template_id = fields.Many2one("product.template")
    weight_done = fields.Boolean(
        string="Weight done old", related="product_template_id.weight_done", store=True
    )
    weight_done_new = fields.Boolean(
        string="Weight done", related="product_template_id.weight_done", store=True
    )
    weight = fields.Float(string="Weight")
