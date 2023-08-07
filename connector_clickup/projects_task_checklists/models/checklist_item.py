from odoo import fields, models


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
        """Change state field to done"""
        self.write({"state": "done"})

    def reset_stage(self):
        """Change state field to todo"""
        self.write({"state": "todo"})
