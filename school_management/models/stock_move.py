from odoo import fields, models, api


class StockMoveInherit(models.Model):
    """To pass the field value from SO to DO"""

    _inherit = "stock.move"

    product_template_id = fields.Many2one("sale.order.line")
    weight_done_new = fields.Boolean(
        string="Weight done", related="sale_line_id.weight_done_new", store=True
    )

    weight = fields.Float(string="Weight", related="sale_line_id.weight")

    # @api.model
    # def get_data(self):
    #     data = self.env['sale.order.line'].search([])
    #     weightdata = ""
    #     for rec in data:
    #         weightdata = rec.weight
    #     for record in self:
    #         record.weight = weightdata

    def get_data(self):
        for move in self:
            if not (move.picking_id and move.picking_id.group_id):
                continue
            picking = move.picking_id
            sale_order = (
                self.env["sale.order"]
                .sudo()
                .search([("procurement_group_id", "=", picking.group_id.id)], limit=1)
            )
        for line in sale_order.order_line:
            if line.product_id.id != move.product_id.id:
                continue
            move.update(
                {
                    "weight": line.weight,
                }
            )
