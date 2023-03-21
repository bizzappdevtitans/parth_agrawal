from odoo import fields, models, api


class StockImmediateTransfer(models.TransientModel):
    _inherit = "stock.immediate.transfer"

    def process(self):
        """To pass updated value in stock.move to sale.order.line and reflect
        in the S.O.L. field by clicking validate and apply button in
        delivery order"""
        res = super(StockImmediateTransfer, self).process()
        data = self.env["stock.picking"].search([])
        for move in data.move_lines:
            sale_line = move.sale_line_id
            if sale_line:
                sale_line["weight"] = move.weight
        return res
