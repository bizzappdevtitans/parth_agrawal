from odoo import fields, models


class ClickupProjectTasks(models.Model):
    _name = "clickup.project.tasks"
    _inherits = {"project.task": "odoo_id"}
    _inherit = ["clickup.model"]
    _description = "Clickup project.tasks binding model"

    odoo_id = fields.Many2one(
        "project.task", string="Task", required=True, ondelete="restrict"
    )
