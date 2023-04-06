from odoo import api, fields, models
from datetime import date, datetime
from odoo.exceptions import ValidationError


class CustomClearanceRevision(models.Model):
    """This model show custom clearance revision for particular customer clearance"""
    _name = "custom.clearance.revision"
    _description = "Custom Clearance Revision"

    name = fields.Char("Name")

    name = fields.Char()
    reason = fields.Text()
    clearance_id = fields.Many2one("custom.clearance")
    last_date = fields.Date(string="Last Date of Submission")
    current = fields.Date(default=datetime.today())

    @api.model
    def duedate_message(self):
        for custom_revision in self.search([]):
            today = date.today()
            print(today)
            if today == custom_revision.last_date:
                email_template_id = self.env.ref(
                    "freight_management.duedate_email_template"
                ).id
                template = self.env["mail.template"].browse(email_template_id)
                result = template.send_mail(custom_revision.id, force_send=True)

    @api.constrains("last_date")
    def _check_date(self):
        """check expected date to reach to be current of future date"""
        for custom_revision in self:
            if custom_revision.last_date < custom_revision.current:
                raise ValidationError("Due date must not be past date")
