from odoo import fields, models


class SaleOrderInheritMail(models.Model):
    _inherit = "sale.order"

    attachment_count = fields.Many2many("ir.attachment", compute="_compute_attachments")

    def _compute_attachments(self):
        attachment_count = self.env["ir.attachment"].search(
            [("res_model", "=", self._name), ("res_id", "=", self.id)]
        )
        self.attachment_count = attachment_count.ids

    def action_quotation_send(self):

        print("also coming here")

        lines = []

        attachment = self.env["ir.attachment"].search(
            [("res_model", "=", self._name), ("res_id", "=", self.id)]
        )

        for order in attachment:
            value = order
            lines.append(value)
        print("\n\n", lines)

        data = {
            "default_model": "sale.order",
            "default_res_id": self.id,
            "default_use_template": bool(
                self.env.ref("sale.mail_template_sale_confirmation", False)
            ),
            "default_template_id": self.env.ref(
                "sale.mail_template_sale_confirmation", False
            ).id,
            "default_composition_mode": "comment",
            "force_email": True,
            "mark_so_as_sent": True,
            "attachment_ids": lines,
        }

        print("\n\n", data)

        compose_form = self.env.ref("mail.email_compose_message_wizard_form", False)

        answer = {
            "name": ("Compose Email"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": data,
        }

        print("\n\n", answer)
        return answer
