from odoo import fields, models, api


class SaleAdvancePaymentInv(models.TransientModel):
    """To pass value from SO to Invoice that is in downpayment option"""

    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        """To pass value from So to invoice that is in
        downpayment option like percentage or fixed"""
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(
            order, so_line, amount
        )
        invoice["invoice_description"] = order.invoice_description
        return invoice
