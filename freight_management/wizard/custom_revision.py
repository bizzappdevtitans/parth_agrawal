from werkzeug import urls
from odoo import models, fields, _


class CustomClearanceRevisionReason(models.TransientModel):
    """This wizard is helpful to create clearance revision"""
    _name = "custom.clearance.revision.wizard"
    _description = "Custom Clearance Revision"

    name = fields.Text("Reason", required=True)
    custom_id = fields.Many2one("custom.clearance")
    text = fields.Char()
    last_date = fields.Date(string="Last Date To Submit")

    def create_revision(self):
        """create revision and send mail if revision created"""
        for rec in self.custom_id:

            mail_content = _(
                "Hi %s,<br>" "The Custom Clearance Revision with reason: %s"
            ) % (rec.agent_id.name, self.name)
            main_content = {
                "subject": _("Custom Clerance Revision For %s")
                % self.custom_id.freight_id.name,
                "author_id": self.env.user.partner_id.id,
                "body_html": mail_content,
                "email_to": rec.agent_id.email,
            }
            mail_id = self.env["mail.mail"].create(main_content)
            mail_id.mail_message_id.body = mail_content
            mail_id.send()

            self.env["custom.clearance.revision"].create(
                {
                    "clearance_id": self.custom_id.id,
                    "reason": self.name,
                    "name": "RE: " + self.custom_id.name,
                    "last_date": self.last_date,
                }
            )
