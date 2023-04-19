from odoo import models
from odoo.exceptions import ValidationError


class CreateDataWizard(models.TransientModel):
    """Wizard to create new Sale Order"""

    _name = "create.data.wizard"
    _description = "create data using wizard"

    def get_payload(self):
        """This method contains the sale order payload"""
        payload = {
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
        return payload

    def action_on_click_create(self):
        """This method use payload to create new sale order"""
        payload = self.get_payload()
        customer = self.env["res.partner"].search(
            [("name", "=", payload["customer"]["name"])]
        )

        if not customer:
            customer = self.env["res.partner"].create(
                {
                    "name": payload["customer"]["name"],
                    "city": payload["customer"]["address"]["city"],
                    "zip": payload["customer"]["address"]["zip"],
                    "phone": payload["customer"]["address"]["phone"],
                }
            )

        order_lines = []

        for line in payload["sale_lines"]:
            product = self.env["product.product"].search(
                [("default_code", "=", line["productId"])]
            )
            if not product:
                raise ValidationError(
                    f"Product with default_code '{line['productId']}' not found"
                )
            order_lines.append(
                (0, 0, {"product_id": product.id, "product_uom_qty": line["quantity"]})
            )

        sale_order = self.env["sale.order"].create(
            {
                "name": payload["name"],
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
