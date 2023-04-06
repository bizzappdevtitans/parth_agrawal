from odoo import fields, models

class FreightServiceLine(models.Model):
    """This model allow to choose different vendors for particular service"""
    _name = 'freight.service.line'
    _description = "Freight Service Line"

    partner_id = fields.Many2one('res.partner', string="Vendor")
    sale = fields.Float('Sale Price')
    line_id = fields.Many2one('freight.service')
