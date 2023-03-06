from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    # sale_id = fields.Many2one("sale.order")
    # manufacturing_description = fields.Char('sale_id.manufacturing_description')

    def _prepare_mo_vals(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
        bom,
    ):
        Movalue = super(StockRule, self)._prepare_mo_vals(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
            bom,
        )
        sale_order = self.env["sale.order"].search([("name", "=", origin)])
        if sale_order:
            Movalue["manufacturing_description"] = sale_order.manufacturing_description
        print(Movalue)
        return Movalue

    # def _prepare_purchase_order(self, company_id, origins, values):
    #     values1 = super(StockRule, self)._prepare_purchase_order(
    #         company_id, origins, values
    #     )
    #     sale_order = self.env["sale.order"].search([("name", "=", origins)])
    #     if sale_order:
    #         values1["purchase_des"] = sale_order.purchase_description
    #     print(values1)
    #     return values1
