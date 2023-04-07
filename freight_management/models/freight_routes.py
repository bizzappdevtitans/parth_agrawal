from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class FreightRoutes(models.Model):
    """This model allows to create new operation routes for freight order"""
    _name = 'freight.routes'
    _description = "Freight Routes"

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
    land_sale = fields.Float('Sale Price for Land', required=True)
    air_sale = fields.Float('Sale Price for Air', required=True)
    water_sale = fields.Float('Sale Price for Water', required=True)
