from odoo import api, fields, models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    attachment_details = fields.Many2many(
        "ir.attachment",
        string="Chatter Attachments",
    )

    def get_mail_values(self, res_ids):
        res = super().get_mail_values(res_ids)
        if self.attachment_details.ids and self.model:
            res[res_ids[0]].setdefault("attachment_ids", []).extend(
                self.attachment_details.ids
            )
        return res

    just = fields.Many2one("sale.order.line")

    order_line_many2many = fields.Many2many(
        related="just.custom_field", string="Product Attachments", readonly=False
    )

    # order_line_many2many = fields.Many2many(
    #     "ir.attachment", string="Product Attachments", readonly=False
    # )

    # product_id = fields.Many2one("product.product", string="Product")

    # @api.model
    # def default_get(self, fields):
    #     res = super(MailComposeMessage, self).default_get(fields)
    #     if (
    #         "attachment_ids" in fields
    #         and res.get("model") == "sale.order"
    #         and self.product_id
    #     ):
    #         order_id = res.get("res_id")
    #         if order_id:
    #             order = self.env["sale.order"].browse(order_id)
    #             attachments = order.mapped("order_line.custom_field").filtered(
    #                 lambda a: self.product_id in a.product_ids
    #             )
    #             res["order_line_many2many"] = [(6, 0, attachments.ids)]
    #             print("\n\n\n", res)
    #     return res

    # product_attachment_ids_aa = fields.Many2many("product.product")

    # product_attachment_ids = fields.Many2many(
    #     related="product_attachment_ids_aa.attachment_ids",
    #     string="product_attachments",
    #     readonly=False,
    #     domain=[("id", "in", "order_id")],
    # )
    # [('id', 'in', order.mapped('order_line.product_id.res_id').ids)]

    # @api.model
    # def default_get(self, fields):
    #     res = super(MailComposeMessage, self).default_get(fields)
    #     active_ids = self._context.get("active_ids")
    #     if active_ids and "order_line_many2many" in fields:
    #         order_lines = self.env["sale.order.line"].search([("id", "in", active_ids)])
    #         custom_field_values = order_lines.mapped("custom_field")
    #         res["order_line_many2many"] = [(6, 0, custom_field_values.ids)]
    #     return res
