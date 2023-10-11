from odoo import fields, models, api


class StockMoveLineInherit(models.Model):
    """To pass the field value from SO to DO"""

    _inherit = "stock.move.line"

    # weight_done_new = fields.Boolean(
    #     string="Weight done", related="sale_line_id.weight_done_new", store=True
    # )

    weight = fields.Float(string="Weight")
