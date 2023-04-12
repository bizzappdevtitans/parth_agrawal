from odoo import fields, models


class SaleOrderInheritMail(models.Model):
    _inherit = "sale.order"

    attachment_count = fields.Many2many("ir.attachment", compute="_compute_attachments")

    def _compute_attachments(self):
        attachment_count = self.env["ir.attachment"].search(
            [("res_model", "=", self._name), ("res_id", "=", self.id)]
        )
        self.attachment_count = attachment_count.ids

