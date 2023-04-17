from odoo import fields, models, api


class SaleOrderInheritMail(models.Model):
    _inherit = "sale.order"

    attachment_count = fields.Many2many("ir.attachment", compute="_compute_attachments")

    def _compute_attachments(self):
        attachment_count = self.env["ir.attachment"].search(
            [("res_model", "=", self._name), ("res_id", "=", self.id)]
        )
        self.attachment_count = attachment_count.ids

    product_attachments = fields.Many2many(
        "ir.attachment",
        compute="_compute_product_attachments",
        string="Product Attachments",
        store=True,
    )

    @api.depends("order_line.product_id.attachment_ids")
    def _compute_product_attachments(self):
        for order in self:
            attachments = self.env["ir.attachment"]
            for line in order.order_line:
                if line.product_id:
                    product_attachments = line.product_id.attachment_ids.filtered(
                        lambda att: att.res_model == "product.product"
                        and att.res_id == line.product_id.id
                    )
                    attachments |= product_attachments
            order.product_attachments = attachments

    def action_quotation_send(self):
        self.ensure_one()
        template = self.env['mail.template'].search([('name', '=', 'Sale Order - Send by Email')], limit=1)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='sale.order',
            default_res_id=self.ids[0],
            default_use_template=bool(template),
            default_template_id=template.id if template else False,
            default_attachment_product=self.product_attachments.ids,
            mark_invoice_as_sent=self.env.context.get('mark_invoice_as_sent', False),
            custom_layout="mail.mail_notification_paynow",
            force_email=True
        )
        return {
            'name': 'Compose Email',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': compose_form.id,
            'view_type': 'form',
            'res_model': 'mail.compose.message',
            'context': ctx,
            'target': 'new',
        }
