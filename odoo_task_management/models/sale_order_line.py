from odoo import fields, models, api


class SaleOrderLineInheritMail(models.Model):
    _inherit = "sale.order.line"


    product_attachments = fields.Many2many(
        "ir.attachment",
        string="Product Attachments",
        store=True,
        compute="_compute_product_attachments",
    )

    @api.depends("product_id.message_ids.attachment_ids")
    def _compute_product_attachments(self):
        for line in self:
            attachments = line.product_id.attachment_ids.filtered(
                lambda att: att.res_model == "product.product"
                and att.res_id == line.product_id.id
            )
            line.product_attachments = [(6, 0, attachments.ids)]
