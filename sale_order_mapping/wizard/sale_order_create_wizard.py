from odoo import models
from odoo.exceptions import ValidationError


class CreateSaleOrderWizard(models.TransientModel):
    _name = "sale.order.create.wizard"
    _description = "create sale order through wizard"

    def get_sale_order_payload(self):
        """This method return the sale order's payload"""
        sale_order_payload = {
            "name": "PL/AT:123456",
            "customer": {
                "name": "XYZ",
                "address": {"city": "Pune", "zip": "10ji033", "phone": "990022933"},
            },
            "sale_lines": [
                {"productId": "5112976146", "quantity": 3},
                {"productId": "5112974885", "quantity": 15},
                {"productId": "5112973994", "quantity": 3},
            ],
        }
        return sale_order_payload

    def action_on_click_create(self):
        """This method use sale order's payload to create new sale order"""
        sale_order_payload = self.get_sale_order_payload()

        customer = self.env["res.partner"].search(
            [("name", "=", sale_order_payload.get("customer").get("name"))], limit=1
        )

        if not customer:
            customer = self.env["res.partner"].create(
                {
                    "name": sale_order_payload.get("customer").get("name"),
                    "city": sale_order_payload.get("customer")
                    .get("address")
                    .get("city"),
                    "zip": sale_order_payload.get("customer").get("address").get("zip"),
                    "phone": sale_order_payload.get("customer")
                    .get("address")
                    .get("phone"),
                }
            )

        order_lines = []
        for line in sale_order_payload.get("sale_lines"):
            product = self.env["product.product"].search(
                [("default_code", "=", line.get("productId"))]
            )
            if not product:
                raise ValidationError(
                    f"Product with default_code '{line.get('productId')}' not found"
                )
            order_lines.append(
                (
                    0,
                    0,
                    {"product_id": product.id, "product_uom_qty": line.get("quantity")},
                )
            )

        sale_order = self.env["sale.order"].create(
            {
                "name": sale_order_payload.get("name"),
                "partner_id": customer.id,
                "order_line": order_lines,
            }
        )
        data = {
            "name": "Sale Order",
            "view_mode": "tree,form",
            "res_model": "sale.order",
            "res_id": sale_order.id,
            "type": "ir.actions.act_window",
        }

        return data
