from odoo import fields, models, api


class StockImmediateTransfer(models.TransientModel):
    _inherit = "stock.immediate.transfer"

    picking_type_id = fields.Many2one("stock.picking")
    generate_invoice = fields.Boolean(
        string="Generate Invoice", related="picking_type_id.generate_invoice"
    )
    product_id = fields.Many2one("product.product")
    product = fields.Char("product_id.name")

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

        if self.generate_invoice == True:
            print("Invoice will be printed because generate invoice is true")
            store = self.env["sale.advance.payment.inv"].search([])
            for rec in store:
                rec.create_invoices()

        if self.generate_invoice == False:
            print("Invoice will not be printed because generate invoice is false")
            pass
        return res
