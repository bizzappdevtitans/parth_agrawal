from odoo import fields, models

class FreightService(models.Model):
    """This model allows to create different services"""
    _name = 'freight.service'
    _description = "Freight Service"

    name = fields.Char('Name', required=True)
    sale_price = fields.Float('Sale Price', required=True)
    line_ids = fields.One2many('freight.service.line', 'line_id')
    partner_info_id = fields.Many2one(related='line_ids.partner_id',readonly=False)
