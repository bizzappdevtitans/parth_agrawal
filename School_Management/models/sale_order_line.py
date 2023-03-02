from odoo import fields, models


class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    available = fields.Boolean(string="Available")
    # saleid = fields.Many2one("sale.order")
    # purchase_description = fields.Char(
    #     string="Purchase order description"
    # )

    # def _prepare_purchase_order(self):
    #     values = super(sale_order_line, self)._prepare_purchase_order()
    #     print("sevice generation inherited")
    #     values["purchase_description"] = self.order_id.purchase_description
    #     # sale_line_purchase_map.update(values)
    #     print(values)
    #     return values

    # def _purchase_service_generation(self):
    #     print("Inherited service generation starts")
    #     POvalues = super(sale_order_line, self)._purchase_service_generation()
    #     POvalues.create({"purchase_description": self.purchase_description})
    #     return POvalues

    # def _purchase_get_date_order(self):
    #     POvalues = super(sale_order_line, self)._purchase_get_date_order()
    #     POvalues["purchase_description"] = self.purchase_description
    #     return POvalues

