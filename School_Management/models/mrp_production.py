from odoo import fields, models


class ManufacturingInherit(models.Model):
    _inherit = "mrp.production"

    manufacturing_description = fields.Char(string="Manufacturing description")

