from odoo import api, fields, models


class TaskChecklist(models.Model):
    _name = "task.checklist"
    _description = "Task Checklist"

    name = fields.Char(string="Checklist Name")
    project_id = fields.Many2one("project.project", string="Project")
    task_id = fields.Many2one("project.task", string="Task")
    checklist_ids = fields.One2many(
        "checklist.item", "checklist_id", string="CheckList Items", required=True
    )


class ChecklistItem(models.Model):
    _name = "checklist.item"
    _description = "Checklist Item"

    name = fields.Char(required=True)
    checklist_item = fields.Char()
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

    checklist_id = fields.Many2one("task.checklist", string="Checklist")
    checklist_ids = fields.Many2many("task.checklist", string="Checklists")
    checklists = fields.One2many(
        "checklist.item",
        compute="_compute_checklist_items",
        string="CheckList Items",
    )

    @api.depends("checklist_ids.checklist_ids")
    def _compute_checklist_items(self):
        """Get checklist items"""
        for record in self:
            self.checklists = [(6, 0, record.checklist_ids.mapped("checklist_ids").ids)]

    # checklist_ids = fields.One2many("checklist.item", "project_id", string="Checklists")
    # checklists = fields.One2many(
    #     "checklist.item",
    #     compute="_compute_checklist_items",
    #     string="CheckList Items",
    # )

    # @api.depends("checklist_ids")
    # def _compute_checklist_items(self):
    #     """Get checklist items"""
    #     for record in self:
    #         self.checklists = record.checklist_ids

    # @api.onchange("checklist_ids")
    # def _onchange_project_id(self):
    #     self.checklists = []
    #     for rec in self.checklist_ids:
    #         checklist = self.env["task.checklist"].search(
    #             [("id", "=", rec.checklist_ids.id)]
    #         )
    #         for rec in checklist:
    #             self.checklists += rec.checklist_ids.checklist_ids.ids
