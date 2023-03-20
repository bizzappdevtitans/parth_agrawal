from odoo import fields, models, api


class DeliveryOrderInherit(models.Model):
    """To pass the field value from SO to DO"""

    _inherit = "stock.picking"

    sale_id = fields.Many2one("sale.order")
    delivery_description = fields.Char(
        string="Delivery Description", related="sale_id.delivery_description"
    )

    def button_validate(self):
        res = super(DeliveryOrderInherit, self).button_validate()
        stock_move = self.env["stock.move"].search([("product_id", "=", self.id)])
        weight = 0.0
        for rec in stock_move:
            weight = rec.weight
        sale_order_line = self.env["sale.order.line"]
        for rec in sale_order_line:
            rec.weight = weight
        return res
