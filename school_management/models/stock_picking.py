from odoo import fields, models, api


class DeliveryOrderInherit(models.Model):
    """To pass the field value from SO to DO"""

    _inherit = "stock.picking"

    sale_id = fields.Many2one("sale.order")
    delivery_description = fields.Char(
        string="Delivery Description"
    )
