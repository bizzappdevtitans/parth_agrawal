from werkzeug import urls
from odoo import api, fields, models, _


class CustomClearance(models.Model):
    _name = "custom.clearance"
    _description = "Custom Clearance"

    name = fields.Char("Name", compute="_compute_name")
    freight_id = fields.Many2one("freight.order", required=True)
    date = fields.Date("Date")
    agent_id = fields.Many2one("res.partner", "Agent", required=True)
    loading_port_id = fields.Many2one("freight.port", string="Loading Port")
    discharging_port_id = fields.Many2one("freight.port", string="Discharging Port")
    line_ids = fields.One2many("custom.clearance.line", "line_id")
    state = fields.Selection(
        [("draft", "Draft"), ("confirm", "Confirm"), ("done", "Done")], default="draft"
    )
    last_date = fields.Date(string="Last Date To Submit")

    @api.depends("freight_id")
    def _compute_name(self):
        """Compute the name of custom clearance"""
        for custom_clearance in self:
            if custom_clearance.freight_id:
                custom_clearance.name = "CC - " + str(custom_clearance.freight_id.name)
            else:
                custom_clearance.name = "CC - "

    @api.onchange("freight_id")
    def _onchange_freight_id(self):
        """Getting default values for loading and discharging port"""
        for custom_clearance in self:
            custom_clearance.date = custom_clearance.freight_id.order_date
            custom_clearance.loading_port_id = custom_clearance.freight_id.loading_port_id
            custom_clearance.discharging_port_id = custom_clearance.freight_id.discharging_port_id
            custom_clearance.agent_id = custom_clearance.freight_id.agent_id

    def action_confirm(self):
        """Send mail to inform agents to custom clearance is confirmed"""
        for custom_clearance in self:
            custom_clearance.name = "CC" " - " + custom_clearance.freight_id.name
            custom_clearance.state = "confirm"

            mail_content = _("Hi %s,<br>" "The Custom Clearance %s is confirmed") % (
                custom_clearance.agent_id.name,
                custom_clearance.name,
            )
            main_content = {
                "subject": _("Custom Clerance For %s") % self.freight_id.name,
                "author_id": self.env.user.partner_id.id,
                "body_html": mail_content,
                "email_to": custom_clearance.agent_id.email,
            }
            mail_id = self.env["mail.mail"].create(main_content)
            mail_id.mail_message_id.body = mail_content
            mail_id.send()

    def action_revision(self):
        """Creating custom revision"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Received/Delivered",
            "view_mode": "form",
            "target": "new",
            "res_model": "custom.clearance.revision.wizard",
            "context": {"default_custom_id": self.id},
        }

    def get_revision(self):
        """Getting details of custom revision"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Custom Revision",
            "view_mode": "tree,form",
            "res_model": "custom.clearance.revision",
            "domain": [("clearance_id", "=", self.id)],
            "context": "{'create': False}",
        }
