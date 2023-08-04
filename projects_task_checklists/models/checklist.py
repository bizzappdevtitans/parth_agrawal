from odoo import api, fields, models


class TaskChecklist(models.Model):
    _name = "task.checklist"
    _description = "Task Checklist"

    name = fields.Char(string="Checklist Name")
    task_id = fields.Many2one("project.task", string="Task")
    checklist_ids = fields.One2many(
        "checklist.item", "checklist_id", string="CheckList Items", required=True
    )


class ChecklistItem(models.Model):
    _name = "checklist.item"
    _description = "Checklist Item"

    name = fields.Char(required=True)
    task_id = fields.Many2one("project.task")
    checklist_id = fields.Many2one("task.checklist")
    parent_checklist = fields.Char(related="checklist_id.name")
    state = fields.Selection(
        string="Status",
        required=True,
        readonly=True,
        copy=False,
        selection=[
            ("todo", "To Do"),
            ("done", "Done"),
        ],
        default="todo",
    )

    def mark_completed(self):
        self.write({"state": "done"})

    def reset_stage(self):
        self.write({"state": "todo"})


class ChecklistProgress(models.Model):
    _inherit = "project.task"

    checklist_ids = fields.One2many("task.checklist", "task_id", string="Checklists")
    checklist_item_ids = fields.One2many(
        "checklist.item",
        compute="_compute_checklist_items",
        string="CheckList Items",
    )

    checklist_progress = fields.Float(
        compute="_compute_checklist_progress",
        string="Checklist Progress",
        store=True,
    )

    @api.depends("checklist_ids.checklist_ids")
    def _compute_checklist_items(self):
        """Get checklist items"""
        for record in self:
            self.checklist_item_ids = [
                (6, 0, record.checklist_ids.mapped("checklist_ids").ids)
            ]

    @api.depends("checklist_ids.checklist_ids.state")
    def _compute_checklist_progress(self):
        """Calculate checklist progress"""
        for record in self:
            total_items = len(record.checklist_item_ids)
            if total_items > 0:
                completed_items = record.checklist_item_ids.filtered(
                    lambda item: item.state == "done"
                )
                progress = (len(completed_items) / total_items) * 100
                record.checklist_progress = progress
            else:
                record.checklist_progress = 0.0
