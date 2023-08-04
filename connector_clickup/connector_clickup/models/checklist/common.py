from odoo import api, fields, models

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

    @api.model
    def create(self, vals):
        """to set the task_id in checklist.
        while importing task for the first time
        - added here as in mapping no binding exists
         to identify based on external id"""
        if not vals.get("task_id"):
            task_checklist_id = vals.get("task_checklist_id")
            if not task_checklist_id:
                return super().create(vals)
            binding = self.env["clickup.project.task"].browse(task_checklist_id)
            vals["task_id"] = binding.odoo_id.id
        return super().create(vals)

    @api.model
    def write(self, vals):
        """If user removed the checklists from particular task,
        at the time of updating or re-importing the tasks the
        co-related checklists will be set in that task again"""
        if not vals.get("task_id"):
            task_checklist_id = self.task_checklist_id.id
            if not task_checklist_id:
                return super().write(vals)
            binding = self.env["clickup.project.task"].browse(task_checklist_id)
            vals["task_id"] = binding.odoo_id.id
        return super().write(vals)


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
        readonly=True,
    )


class TaskChecklistAdapter(Component):
    _name = "clickup.task.checklist.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.task.checklist"
    _clickup_model = None
    _clickup_ext_id_key = "id"
