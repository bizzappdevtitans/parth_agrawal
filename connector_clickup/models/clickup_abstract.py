from odoo import fields, models


class ClickupAbstractModel(models.AbstractModel):
    _name = "clickup.model"
    _description = "Clickup abstract model"

    clickup_backend_id = fields.Many2one("clickup.backend", string="Clickup Backend")
    external_id = fields.Char(string="External ID")
    api_token_data = fields.Char(string="API token")
    created_at = fields.Datetime(string="Created At")
