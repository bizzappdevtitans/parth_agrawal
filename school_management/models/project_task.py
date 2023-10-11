from odoo import fields, models, api


class TaskInherit(models.Model):
    """To Pass the value from SO to Task"""

    _inherit = "project.task"

    project_id = fields.Many2one("project.project")
    task_description = fields.Char(
        string="Project/Task Description", related="project_id.task_description"
    )
