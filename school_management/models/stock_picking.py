from odoo import fields, models, api


class DeliveryOrderInherit(models.Model):
    """To pass the field value from SO to DO"""

    _inherit = "stock.picking"

    sale_id = fields.Many2one("sale.order")
    delivery_description = fields.Char(string="Delivery Description")
    picking_type_id = fields.Many2one("stock.picking.type")
    generate_invoice = fields.Boolean(
        string="Generate Invoice", related="picking_type_id.generate_invoice"
    )

    # def button_validate(self):
    #     values = super(DeliveryOrderInherit, self).button_validate()
    #     if self.generate_invoice == True:
    #         print("Invoice will be printed because generate invoice is true")
    #         self.env["sale.advance.payment.inv"].create_invoices()
    #         # for record in data:
    #         #     record.create_invoices()
    #     if self.generate_invoice == False:
    #         print("Invoice will not be printed because generate invoice is false")
    #     return values
