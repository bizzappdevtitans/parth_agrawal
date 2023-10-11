from odoo import fields, models, api


class StockPickingType(models.Model):
    """To pass the field value from SOL to stock.move"""

    _inherit = "stock.picking.type"

    generate_invoice = fields.Boolean(string="Generate Invoice")
