from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FreightOrderServiceLine(models.Model):
    _name = "freight.order.service"
    _description = "Freight Order Service"

    line_id = fields.Many2one("freight.order")
    service_id = fields.Many2one("freight.service", required=True)
    partner_id = fields.Many2one("res.partner", related="service_id.partner_info_id", string="Vendor",readonly=False)
    qty = fields.Float("Quantity")
    cost = fields.Float("Cost")
    sale = fields.Float("Sale")
    total_sale = fields.Float("Total Sale")

    @api.onchange("service_id", "partner_id")
    def _onchange_partner_id(self):
        """Calculate the price of services"""
        for freight_service in self:
            if freight_service.service_id:
                if freight_service.partner_id:
                    if freight_service.service_id.line_ids:
                        for service in freight_service.service_id.line_ids:
                            if freight_service.partner_id == service.partner_id:
                                freight_service.sale = service.sale
                            else:
                                freight_service.sale = freight_service.service_id.sale_price
                    else:
                        freight_service.sale = freight_service.service_id.sale_price
                else:
                    freight_service.sale = freight_service.service_id.sale_price

    @api.onchange("qty", "sale")
    def _onchange_qty(self):
        """Calculate the subtotal of route operation"""
        for freight_service in self:
            freight_service.total_sale = freight_service.qty * freight_service.sale

