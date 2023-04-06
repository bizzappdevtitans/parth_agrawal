from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Tracking(models.Model):
    """This model will take data regarding freight order tracking status"""
    _name = "freight.track"
    _description = "Freight Track"

    source_loc = fields.Many2one("freight.port", "Source Location")
    destination_loc = fields.Many2one("freight.port", "Destination Location")
    transport_type = fields.Selection(
        [("land", "Land"), ("air", "Air"), ("water", "Water")], "Transport"
    )
    track_id = fields.Many2one("freight.order")
    date = fields.Date("Date")
    type = fields.Selection(
        [("received", "Received"), ("delivered", "Delivered")], "Received/Delivered"
    )
