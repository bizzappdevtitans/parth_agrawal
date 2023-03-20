from odoo import fields, models


class StockRule(models.Model):
    """To pass the field value from SO to MO using stock.rule model's method"""

    _inherit = "stock.rule"

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
        """This method helps to pass value from SO to manufacturing order"""
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
