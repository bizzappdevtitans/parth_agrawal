from odoo import fields, models


class ClickupProjectProject(models.Model):
    _name = "clickup.project.project"
    _inherits = {"project.project": "odoo_id"}
    _inherit = ["clickup.model"]
    _description = "Clickup project.project binding model"

    odoo_id = fields.Many2one(
        "project.project", string="Project", required=True, ondelete="restrict"
    )
