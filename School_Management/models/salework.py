from odoo import fields, models, api


class SaleWork(models.Model):
    _name = "sale.work"
    _description = "inherited fees model"

    feesstatus = fields.Selection(
        [
            ("paid", "Paid"),
            ("unpaid", "Unpaid"),
        ],
        string="Payment Status",
    )


# -------------------------------------------------------------------------------------------


class Paymentinfeestructure(models.Model):
    _inherit = "fees.option"

    feesstatus = fields.Selection(
        [
            ("paid", "Paid"),
            ("unpaid", "Unpaid"),
        ],
        string="Payment Status",
    )


# -------------------------------------------------------------------------------------------


# class SaleOrderLine(models.Model):
#     _inherit = "sale.order.line"

#     available = fields.Boolean(string="Available")


# -------------------------------------------------------------------------------------------

# class SaleOrderInherit(models.Model):
#     _inherit = "sale.order"

#     feesstatus = fields.Selection(
#         [
#             ("paid", "Paid"),
#             ("unpaid", "Unpaid"),
#         ],
#         string="Payment Status",
#     )

#     delivery_description = fields.Char("Delivery Description")
#     invoice_description = fields.Char("Invoice Description")

#     def _prepare_invoice(self):
#         invoice_dec = super(SaleOrderInherit, self)._prepare_invoice()
#         invoice_dec["invoice_description"] = self.invoice_description
#         return invoice_dec

#     # def action_confirm(self):

#     #     res = super(SaleOrderInherit, self).action_confirm()

#     #     for addin in self.picking_ids:

#     #         addin.write({"delivery_description": self.delivery_description})

#     #     return res

#     def _prepare_picking_vals(self):
#         picking_vals = super(SaleOrderInherit, self)._prepare_picking_vals()
#         picking_vals["delivery_description"] = self.delivery_description
#         return picking_vals


# -------------------------------------------------------------------------------------------


# class SaleAdvancePaymentInv(models.TransientModel):
#     _inherit = "sale.advance.payment.inv"

#     def _create_invoice(self, order, so_line, amount):
#         invoice = super(SaleAdvancePaymentInv, self)._create_invoice(
#             order, so_line, amount
#         )
#         invoice["invoice_description"] = order.invoice_description
#         return invoice


# -------------------------------------------------------------------------------------------


# class DeliveryOrderInherit(models.Model):
#     _inherit = "stock.picking"

#     sale_id = fields.Many2one("sale.order")
#     delivery_description = fields.Char(
#         string="Delivery Description", related="sale_id.delivery_description"
#     )


# -------------------------------------------------------------------------------------------


# class InvoiceInherit(models.Model):
#     _inherit = "account.move"

#     invoice_description = fields.Char(string="Invoice Description")


# -------------------------------------------------------------------------------------------
