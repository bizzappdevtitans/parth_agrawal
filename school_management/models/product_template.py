from odoo import fields, models


class Product(models.Model):
    _inherit = "product.template"

    weight_done = fields.Boolean(
        string="Weight done"
    )
