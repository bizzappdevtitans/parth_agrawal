from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class FreightOrderLine(models.Model):
    _name = "freight.order.line"
    _description = "Freight Order Line"

    order_id = fields.Many2one("freight.order")
    container_id = fields.Many2one(
        "freight.container", string="Container", domain="[('state', '=', 'available')]"
    )
    product_id = fields.Many2one("product.product", string="Goods")
    billing_type = fields.Selection(
        [("weight", "Weight"), ("volume", "Volume")], string="Billing On"
    )
    pricing_id = fields.Many2one("freight.price", string="Pricing")
    price = fields.Float("Unit Price")
    total_price = fields.Float("Total Price")
    volume = fields.Float("Volume")
    weight = fields.Float("Weight")

    @api.constrains("weight")
    def _check_weight(self):
        """Checking the weight of containers"""
        for freight_order_line in self:
            if freight_order_line.container_id and freight_order_line.billing_type:
                if freight_order_line.billing_type == "weight":
                    if freight_order_line.container_id.weight < freight_order_line.weight:
                        raise ValidationError(
                            "The weight is must be less "
                            "than or equal to %s" % (freight_order_line.container_id.weight)
                        )

    @api.constrains("volume")
    def _check_volume(self):
        """Checking the volume of containers"""
        for freight_order_line in self:
            if freight_order_line.container_id and freight_order_line.billing_type:
                if freight_order_line.billing_type == "volume":
                    if freight_order_line.container_id.volume < freight_order_line.volume:
                        raise ValidationError(
                            "The volume is must be less "
                            "than or equal to %s" % (freight_order_line.container_id.volume)
                        )

    @api.onchange("pricing_id", "billing_type")
    def onchange_price(self):
        """Calculate the weight and volume of container"""
        for freight_order_line in self:
            if freight_order_line.billing_type == "weight":
                freight_order_line.volume = 0.00
                freight_order_line.price = freight_order_line.pricing_id.weight
            elif freight_order_line.billing_type == "volume":
                freight_order_line.weight = 0.00
                freight_order_line.price = freight_order_line.pricing_id.volume

    @api.onchange("pricing_id", "billing_type", "volume", "weight")
    def onchange_total_price(self):
        """Calculate sub total price"""
        for freight_order_line in self:
            if freight_order_line.billing_type and freight_order_line.pricing_id:
                if freight_order_line.billing_type == "weight":
                    freight_order_line.total_price = freight_order_line.weight * freight_order_line.price
                elif freight_order_line.billing_type == "volume":
                    freight_order_line.total_price = freight_order_line.volume * freight_order_line.price
