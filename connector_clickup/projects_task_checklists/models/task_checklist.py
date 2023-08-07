from odoo import fields, models


class TaskChecklist(models.Model):
    _name = "task.checklist"
    _description = "Task Checklist"

    name = fields.Char(string="Checklist Name")
    task_id = fields.Many2one("project.task", string="Task")
    checklist_ids = fields.One2many(
        "checklist.item", "checklist_id", string="CheckList Items", required=True
    )
