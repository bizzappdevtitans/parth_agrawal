from odoo import fields, models

from odoo.addons.component.core import Component


class ClickupProjectTaskType(models.Model):
    _name = "clickup.project.task.type"
    _inherits = {"project.task.type": "odoo_id"}
    _inherit = ["clickup.model"]
    _description = "Clickup project.task.type binding model"

    odoo_id = fields.Many2one(
        "project.task.type", string="Stage", required=True, ondelete="restrict"
    )


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
    backend_id = fields.Many2one(
        "clickup.backend",
        related="clickup_bind_ids.backend_id",
        string="Clickup Backend",
        readonly=True,
    )
    api_token_data = fields.Char(
        string="API token",
        readonly=True,
    )


class TaskTypeAdapter(Component):
    _name = "clickup.project.task.type.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.project.task.type"
    _akeneo_model = "clickup.project.task.type"
    _akeneo_ext_id_key = "status"
