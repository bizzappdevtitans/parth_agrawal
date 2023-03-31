from werkzeug import urls
from odoo import fields, models, _


class FreightTracking(models.Model):
    _name = 'freight.order.track'
    _description = "Freight Order Track"

    date = fields.Date('Date', default=fields.Date.today())
    freight_id = fields.Many2one('freight.order')
    source_loc = fields.Many2one('freight.port', 'Source Location')
    destination_loc = fields.Many2one('freight.port', 'Destination Location')
    transport_type = fields.Selection([('land', 'Land'), ('air', 'Air'),
                                       ('water', 'Water')], "Transport")
    type = fields.Selection([('received', 'Received'),
                             ('delivered', 'Delivered')], 'Received/Delivered')

    def order_submit(self):
        """Create tracking details of order"""
        self.env['freight.track'].create({
            'track_id': self.freight_id.id,
            'source_loc': self.source_loc.id,
            'destination_loc': self.destination_loc.id,
            'transport_type': self.transport_type,
            'date': self.date,
            'type': self.type,
        })
        for freight_track in self.freight_id:

            mail_content = _('Hi<br>'
                             'The Freight Order %s is %s at %s'

                             ) % (freight_track.name, self.type,
                                  self.destination_loc.name)
            email_to = self.env['res.partner'].search([
                ('id', 'in', (freight_track.shipper_id.id, freight_track.consignee_id.id,
                              freight_track.agent_id.id))])
            for mail in email_to:
                main_content = {
                    'subject': _('Freight Order %s is %s at %s') % (freight_track.name,
                                                                    self.type,
                                                                    self.destination_loc.name,),
                    'author_id': freight_track.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': mail.email
                }
                mail_id = freight_track.env['mail.mail'].create(main_content)
                mail_id.mail_message_id.body = mail_content
                mail_id.send()


