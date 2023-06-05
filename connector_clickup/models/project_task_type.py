from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"
    _description = "Inherited project.task.type model"

    clickup_bind_ids = fields.One2many(
        "clickup.project.task.type",
        "odoo_id",
        string="Clickup Backend ID",
        readonly=True,
    )
    external_id = fields.Char(
        related="clickup_bind_ids.external_id",
        readonly=True,
    )
    clickup_backend_id = fields.Many2one(
        "clickup.backend",
        related="clickup_bind_ids.clickup_backend_id",
        string="Clickup Backend",
        readonly=True,
    )
    api_token_data = fields.Char(
        string="API token",
        related="clickup_bind_ids.api_token_data",
        readonly=True,
    )
