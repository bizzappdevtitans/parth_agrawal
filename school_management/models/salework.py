from odoo import fields, models, api


class SaleWork(models.Model):
    """To show new field in existing fees option model"""
    _name = "sale.work"
    _description = "inherited fees model"

    feesstatus = fields.Selection(
        [
            ("paid", "Paid"),
            ("unpaid", "Unpaid"),
        ],
        string="Payment Status",
    )


class Paymentinfeestructure(models.Model):
    _inherit = "fees.option"

    feesstatus = fields.Selection(
        [
            ("paid", "Paid"),
            ("unpaid", "Unpaid"),
        ],
        string="Payment Status",
    )
