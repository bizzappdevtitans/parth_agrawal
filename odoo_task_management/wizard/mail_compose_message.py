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
