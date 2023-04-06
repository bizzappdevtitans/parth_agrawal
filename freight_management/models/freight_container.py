from odoo import fields, models


class FreightContainer(models.Model):
    """This model allow to create container records"""
    _name = "freight.container"
    _description = "Freight Container"

    name = fields.Char("Name", required=True)
    code = fields.Char("Code")
    size = fields.Float("Size", required=True)
    size_uom_id = fields.Many2one("uom.uom", string="Size UOM")
    weight = fields.Float("Weight", required=True)
    weight_uom_id = fields.Many2one("uom.uom", string="Weight UOM")
    volume = fields.Float("Volume", required=True)
    volume_uom_id = fields.Many2one("uom.uom", string="Volume UOM")
    active = fields.Boolean("Active", default=True)
    state = fields.Selection(
        [("available", "Available"), ("reserve", "Reserve")], default="available"
    )
