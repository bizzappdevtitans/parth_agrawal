from odoo import fields, models


class ClickupProjectTaskType(models.Model):
    _name = "clickup.project.task.type"
    _inherits = {"project.task.type": "odoo_id"}
    _inherit = ["clickup.model"]
    _description = "Clickup project.task.type binding model"

    odoo_id = fields.Many2one(
        "project.task.type", string="Stage", required=True, ondelete="restrict"
    )
