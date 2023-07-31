from odoo import fields, models

from odoo.addons.component.core import Component


class ClickupChecklistItem(models.Model):
    _name = "clickup.checklist.item"
    _inherit = ["clickup.binding"]
    _inherits = {"checklist.item": "odoo_id"}
    _description = "Clickup Checklist Item binding model"

    odoo_id = fields.Many2one("checklist.item", required=True, ondelete="restrict")
    clickup_checklist_item_id = fields.Many2one("clickup.task.checklist")


class ChecklistItem(models.Model):
    _inherit = "checklist.item"

    clickup_bind_ids = fields.One2many(
        "clickup.checklist.item",
        "odoo_id",
        readonly=True,
    )
    clickup_backend_id = fields.Many2one(
        "clickup.backend",
        related="clickup_bind_ids.backend_id",
        string="Clickup Backend",
        readonly=False,
    )


class ChecklistItemAdapter(Component):
    _name = "clickup.checklist.item.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.checklist.item"
    _clickup_model = None
    _clickup_ext_id_key = "id"
