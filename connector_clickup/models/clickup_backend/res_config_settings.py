from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    clickup_backend_id = fields.Many2one(
        comodel_name="clickup.backend",
        string="Default Clickup Backend",
        related="company_id.clickup_backend_id",
        readonly=False,
    )
