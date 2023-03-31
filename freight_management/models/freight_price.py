from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class FreightPricing(models.Model):
    _name = 'freight.price'
    _description = "Freight Price"

    name = fields.Char('Name', required=True)
    volume = fields.Float('Volume Price', required=True)
    weight = fields.Float('Weight Price', required=True)
