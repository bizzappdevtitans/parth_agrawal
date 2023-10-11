from odoo import fields, models


class ManufacturingInherit(models.Model):
    """To pass the value from SO to MO"""
    _inherit = "mrp.production"

    manufacturing_description = fields.Char(string="Manufacturing description")
