from odoo import fields, models

from odoo.addons.component.core import Component


class AkeneoMetaData(models.AbstractModel):
    _name = "clickup.metadata"
    _rec_name = "team"
    _description = "Clickup Metadata"

    team = fields.Char(string="team", required=True, index=True)
    name = fields.Char(string="name")


class ClickupTeam(models.Model):
    _name = "clickup.team"
    _inherit = ["clickup.binding", "clickup.metadata"]
    _description = "Clickup Team"


class ClickupTeamAdapter(Component):
    _name = "clickup.team.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.team"

    _clickup_model = "/team"
    _odoo_ext_id_key = "external_id"
    _clickup_ext_id_key = "id"
