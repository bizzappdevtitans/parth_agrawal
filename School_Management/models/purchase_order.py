from odoo import fields, models


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    # sale_reference_id = fields.Many2one("sale.order")
    # purchase_description = fields.Char(string="Purchase order description")
    # , related="order_id.purchase_description"
    purchase_des = fields.Char(string="description")
