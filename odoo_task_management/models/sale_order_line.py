from odoo import fields, models, api


class SaleOrderLineInheritMail(models.Model):
    _inherit = "sale.order.line"

    # product_attachments = fields.Many2many(
    #     "ir.attachment", string="Product Attachments"
    # )

    custom_field = fields.Many2many("ir.attachment", string="Attachment in product",readonly=False,store=True)

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            self.custom_field = self.product_id.attachment_ids.ids
        if self.product_id:
            product_id = self.product_id.id
            order_id = self.order_id.id
            template_id = self.env.ref("sale.mail_template_sale_confirmation").id
            email_from = self.env.user.email or ""
            email_to = self.order_id.partner_id.email
            subject = self.order_id.name
            body = self.order_id.note

            product_id = self.env["product.product"].browse(product_id)
            attachment_ids = product_id.attachment_ids.ids
            print("\n\n\n", attachment_ids, "\n\n\n")

            ctx = dict(
                default_model="sale.order",
                default_res_id=order_id,
                default_use_template=bool(template_id),
                default_template_id=template_id,
                mark_so_as_sent=True,
                custom_layout="mail.mail_notification_light",
                force_email=True,
                email_from=email_from,
                email_to=email_to,
                subject=subject,
                body=body,
                attachment_ids=attachment_ids,
            )

            compose_form = self.env.ref("mail.email_compose_message_wizard_form", False)
            data = {
                "name": "Compose Email",
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "mail.compose.message",
                "views": [(compose_form.id, "form")],
                "view_id": compose_form.id,
                "target": "new",
                "context": ctx,
            }
            print(data)

    # @api.onchange("product_id")
    # def onchange_product_id(self):
    #     if self.product_id:
    #         attachments = self.product_id.attachment_ids.id
    #         self.product_attachments = [(6, 0, attachments.ids)]

    # @api.onchange("product_id")
    # def onchange_product_id(self):
    #     if self.product_id:
    #         product_id = self.product_id.id
    #         order_id = self.order_id.id
    #         template_id = self.env.ref("sale.mail_template_sale_confirmation").id
    #         email_from = self.env.user.email or ""
    #         email_to = self.order_id.partner_id.email
    #         subject = self.order_id.name
    #         body = self.order_id.note

    #         product_id = self.env["product.product"].browse(product_id)
    #         attachment_ids = product_id.attachment_ids.ids
    #         print("\n\n\n", attachment_ids, "\n\n\n")

    #         ctx = dict(
    #             default_model="sale.order",
    #             default_res_id=order_id,
    #             default_use_template=bool(template_id),
    #             default_template_id=template_id,
    #             mark_so_as_sent=True,
    #             custom_layout="mail.mail_notification_light",
    #             force_email=True,
    #             email_from=email_from,
    #             email_to=email_to,
    #             subject=subject,
    #             body=body,
    #             attachment_ids=attachment_ids,
    #         )

    #         compose_form = self.env.ref("mail.email_compose_message_wizard_form", False)
    #         data = {
    #             "name": "Compose Email",
    #             "type": "ir.actions.act_window",
    #             "view_mode": "form",
    #             "res_model": "mail.compose.message",
    #             "views": [(compose_form.id, "form")],
    #             "view_id": compose_form.id,
    #             "target": "new",
    #             "context": ctx,
    #         }
    #         print(data)
    #         return data
