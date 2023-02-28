from odoo import fields, models, api


class InvoiceInherit(models.Model):
    _inherit = "account.move"

    invoice_description = fields.Char(string="Invoice Description")
