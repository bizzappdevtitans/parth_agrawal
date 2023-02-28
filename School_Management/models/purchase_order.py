from odoo import fields, models, api


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    sale_order_id = fields.Many2one('sale.order')
    purchase_description = fields.Char(related="sale_order_id.purchase_description",string="Purchase order description")
