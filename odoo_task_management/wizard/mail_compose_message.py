from odoo import api, fields, models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    attachment_details = fields.Many2many(
        "ir.attachment",
        string="Chatter Attachments",
    )

    def get_mail_values(self, res_ids):
        res = super().get_mail_values(res_ids)
        if self.attachment_details.ids or self.attachment_product.ids:
            res[res_ids[0]].setdefault("attachment_ids", []).extend(
                self.attachment_details.ids
            )
            res[res_ids[0]].setdefault("attachment_ids", []).extend(
                self.attachment_product.ids
            )
        return res

    attachment_product = fields.Many2many(
        "ir.attachment",
        "res_id",
        string="Product Attachments",
    )

