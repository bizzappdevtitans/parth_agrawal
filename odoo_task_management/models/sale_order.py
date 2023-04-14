from odoo import fields, models, api


class SaleOrderInheritMail(models.Model):
    _inherit = "sale.order"

    attachment_count = fields.Many2many("ir.attachment", compute="_compute_attachments")

    def _compute_attachments(self):
        attachment_count = self.env["ir.attachment"].search(
            [("res_model", "=", self._name), ("res_id", "=", self.id)]
        )
        self.attachment_count = attachment_count.ids

    custom_field = fields.Many2many("ir.attachment", string="Attachment in product",readonly=False,store=True)

    # @api.onchange("order_line")
    # def onchange_product_id(self):
    #     if self.order_line:
    #         self.product_chatter_attachment = self.order_line.product_id.attachment_ids.ids

    # product_attachments_data = fields.Many2many(
    #     "ir.attachment", string="Product Attachments",readonly=False
    # )

    # def action_confirm(self):
    #     for line in self.order_line:
    #          attachment_count = order_line.env["ir.attachment"].search(
    #         [("res_model", "=", "product.product"), ("res_id", "=", self.id)]
    #      )
    #         self.product_attachments_data = order_line.product_id.attachment_id_lol

    #     print(res)
    #     return res

    # @api.model
    # def create(self, vals):
    #     res = super(SaleOrderInheritMail, self).create(vals)
    #     order_lines = res.order_line.filtered(
    #         lambda l: l.product_id.id == vals.get("product_id")
    #     )
    #     attachment_ids = []
    #     for line in order_lines:
    #         product_attachments = line.product_id.attachment_ids
    #         print("\n\n", product_attachments)
    #         for attachment in product_attachments:
    #             attachment_ids.append(attachment.id)
    #     res.write({"product_attachments_data" : [(6, 0, attachment_ids)]})
    #     return res
