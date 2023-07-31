from odoo import fields, models

from odoo.addons.component.core import Component


class ClickupTaskChecklist(models.Model):
    _name = "clickup.task.checklist"
    _inherit = ["clickup.binding"]
    _inherits = {"task.checklist": "odoo_id"}
    _description = "Clickup Task Checklist binding model"

    odoo_id = fields.Many2one("task.checklist", required=True, ondelete="restrict")
    clickup_checklist_item_ids = fields.One2many(
        comodel_name="clickup.checklist.item",
        inverse_name="clickup_checklist_item_id",
    )

    task_checklist_id = fields.Many2one("clickup.project.task")


class TaskChecklist(models.Model):
    _inherit = "task.checklist"

    clickup_bind_ids = fields.One2many(
        "clickup.task.checklist",
        "odoo_id",
        readonly=True,
    )
    clickup_backend_id = fields.Many2one(
        "clickup.backend",
        related="clickup_bind_ids.backend_id",
        string="Clickup Backend",
        readonly=False,
    )


class TaskChecklistAdapter(Component):
    _name = "clickup.task.checklist.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.task.checklist"
    _clickup_model = None
    _clickup_ext_id_key = "id"
