from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    clickup_backend_id = fields.Many2one(
        "clickup.backend",
        string="Default Clickup Backend",
        related="clickup_project_project.clickup_backend_id",
    )

    clickup_project_project = fields.One2many(
        comodel_name="clickup.project.project", inverse_name="company_id"
    )
