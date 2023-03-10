from odoo import fields, models


class InheritFees(models.Model):
    """Inherit all the fields of feesoption model and add new field in it"""
    _inherit = "fees.option"
    _name = 'inherit.fees'
    _description = "inherited fees model"

    feesstatus = fields.Selection(
        [
            ("paid", "Paid"),
            ("unpaid", "unpaid"),
        ],
        string="Payment Status",
    )
