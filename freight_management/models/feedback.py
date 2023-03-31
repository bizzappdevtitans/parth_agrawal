from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import ValidationError


class Feedback(models.Model):
    """This model store the feedback and show it as a review"""

    _name = "feedback.option"
    _description = "feedback option model"

    freight_order_id = fields.Many2one("freight.order", string="Freight Order")
    name = fields.Many2one(related="freight_order_id.shipper_id", string="Customer Name")
    source_location = fields.Many2one(
        related="freight_order_id.loading_port_id", string="From"
    )
    destination_location = fields.Many2one(
        related="freight_order_id.discharging_port_id", string="To"
    )
    subject = fields.Char("Subject")
    note = fields.Text("Note")
    priority = fields.Selection(
        [
            ("0", "review not given"),
            ("1", "poor"),
            ("2", "Bad"),
            ("3", "Average"),
            ("4", "good"),
            ("5", "Excellent"),
        ],
        "Appreciation",
        default="0",
    )
    date = fields.Date(string="Date", default=datetime.today(), readonly=True)

    _sql_constraints = [
        ('freight_order_id', 'UNIQUE (freight_order_id)',  'Feedback already exist for given freight order!')
    ]
