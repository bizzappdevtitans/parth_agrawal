from odoo import fields, models, api


class StockMoveInherit(models.Model):
    """To pass the field value from SOL to stock.move"""

    _inherit = "stock.move"

    product_temp_id = fields.Many2one("sale.order.line")
    weight_done_new = fields.Boolean(
        string="Weight done", related="sale_line_id.weight_done_new", store=True
    )

    weight = fields.Float(string="Weight")

    def _get_new_picking_values(self):
        """This method helps to pass value from SO to delivery order"""
        picking_vals = super(StockMoveInherit, self)._get_new_picking_values()
        picking_vals[
            "delivery_description"
        ] = self.sale_line_id.order_id.delivery_description
        for move in self:
            move.weight = move.sale_line_id.weight
        return picking_vals
