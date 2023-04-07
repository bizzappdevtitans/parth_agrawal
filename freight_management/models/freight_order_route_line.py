from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FreightOrderRouteLine(models.Model):
    """This model is to create operation route line to use it in freight order"""

    _name = "freight.order.routes.line"
    _description = "Freight Order Routes Line"

    route_id = fields.Many2one("freight.order")
    operation_id = fields.Many2one("freight.routes", required=True)
    source_loc = fields.Many2one("freight.port", "Source Location")
    destination_loc = fields.Many2one("freight.port", "Destination Location")
    transport_type = fields.Selection(
        [("land", "Land"), ("air", "Air"), ("water", "Water")],
        "Transport",
        required=True,
    )
    sale = fields.Float("Sale")

    @api.onchange("operation_id", "transport_type")
    def _onchange_operation_id(self):
        """calculate the price of route operation"""
        for freight_route_line in self:
            if (
                freight_route_line.operation_id
                and freight_route_line.transport_type
                and freight_route_line.transport_type == "land"
            ):
                freight_route_line.sale = freight_route_line.operation_id.land_sale
            if (
                freight_route_line.operation_id
                and freight_route_line.transport_type
                and freight_route_line.transport_type == "air"
            ):
                freight_route_line.sale = freight_route_line.operation_id.air_sale
            if (
                freight_route_line.operation_id
                and freight_route_line.transport_type
                and freight_route_line.transport_type == "water"
            ):
                freight_route_line.sale = freight_route_line.operation_id.water_sale
