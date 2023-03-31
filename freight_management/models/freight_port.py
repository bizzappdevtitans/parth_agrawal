from odoo import fields, models


class FreightPort(models.Model):
    _name = 'freight.port'
    _description = "Freight Port"

    name = fields.Char('Name')
    code = fields.Char('Code')
    state_id = fields.Many2one('res.country.state',
                               domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one('res.country', required=True)
    active = fields.Boolean('Active', default=True)
    land = fields.Boolean('Land')
    air = fields.Boolean('Air')
    water = fields.Boolean('Water')
