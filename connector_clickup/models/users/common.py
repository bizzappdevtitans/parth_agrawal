from odoo import fields, models

from odoo.addons.component.core import Component


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


class UserAdapter(Component):
    _name = "clickup.res.users.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.res.users"
    _clickup_model = "/user"
    _odoo_ext_id_key = "external_id"
    _clickup_ext_id_key = "id"
