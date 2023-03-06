from odoo import fields, models, api


class DeliveryOrderInherit(models.Model):
    _inherit = "stock.picking"

    sale_id = fields.Many2one("sale.order")
    delivery_description = fields.Char(
        string="Delivery Description", related="sale_id.delivery_description"
    )
