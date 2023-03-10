from odoo import fields, models, api


class InvoiceInherit(models.Model):
    '''This class take value from sale order
    and show it in accout.move object.'''
    _inherit = "account.move"

    invoice_description = fields.Char(string="Invoice Description")
