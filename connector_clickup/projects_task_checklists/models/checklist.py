from odoo import api, fields, models


class TaskChecklist(models.Model):
    _name = "task.checklist"
    _description = "Task Checklist"
    name = fields.Char()
    project_id = fields.Many2one("project.project", string="Project")
    task_ids = fields.Many2one("project.task", string="Task")

    checklist_ids = fields.One2many(
        "checklist.item", "checklist_id", string="CheckList Items", required=True
    )


class ChecklistItem(models.Model):
    _name = "checklist.item"
    _description = "Checklist Item"

    name = fields.Char(required=True)
    item_id = fields.Char()
    projects_id = fields.Many2one("project.task")
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
        self.state = "done"

    def reset_stage(self):
        self.state = "todo"


class ChecklistProgress(models.Model):
    _inherit = "project.task"

    checklist_id = fields.Many2one("task.checklist")
    checklists = fields.One2many(
        "checklist.item", "projects_id", string="CheckList Items", required=True
    )

    @api.onchange("checklist_id")
    def _onchange_project_id(self):
        self.checklists = []
        checklist = self.env["task.checklist"].search(
            [("name", "=", self.checklist_id.name)]
        )
        for rec in checklist:
            self.checklists += rec.checklist_ids
