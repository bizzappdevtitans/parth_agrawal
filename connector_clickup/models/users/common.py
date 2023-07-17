from odoo import fields, models


class ClickupUser(models.Model):
    _name = "clickup.res.users"
    _inherit = ["clickup.binding"]
    _inherits = {"res.users": "odoo_id"}
    _description = "Clickup res.users binding model"

    odoo_id = fields.Many2one("res.users", required=True, ondelete="restrict")


class ResUser(models.Model):
    _inherit = "res.users"

    clickup_bind_ids = fields.One2many(
        "clickup.res.users",
        "odoo_id",
        readonly=True,
    )

    clickup_backend_id = fields.Many2one(
        "clickup.backend",
        related="clickup_bind_ids.backend_id",
        string="Clickup Backend",
        readonly=False,
    )
