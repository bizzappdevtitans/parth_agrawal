from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    clickup_backend_id = fields.Many2one(
        "clickup.backend",
        string="Default Clickup Backend",
    )
