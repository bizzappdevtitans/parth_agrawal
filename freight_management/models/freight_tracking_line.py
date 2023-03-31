from werkzeug import urls
from odoo import fields, models, _

class FreightTrackingLine(models.Model):
    _name = 'freight.order.track.line'
    _description = "Freight Order Track Line"

    track_line_id = fields.Many2one('freight.order.track')
    source_loc = fields.Many2one('freight.port', 'Source Location')
    destination_loc = fields.Many2one('freight.port', 'Destination Location')
    transport_type = fields.Selection([('land', 'Land'), ('air', 'Air'),
                                       ('water', 'Water')], "Transport")
    date = fields.Date('Date')
    type = fields.Selection([('receive', 'Received'), ('deliver', 'Delivered')],
                            'Received/Delivered')
