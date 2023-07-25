from odoo import fields, models

from odoo.addons.component.core import Component


class ClickupProjectTaskType(models.Model):
    _name = "clickup.project.task.type"
    _inherits = {"project.task.type": "odoo_id"}
    _inherit = ["clickup.binding"]
    _description = "Clickup project.task.type binding model"

    odoo_id = fields.Many2one(
        "project.task.type", string="Stage", required=True, ondelete="restrict"
    )


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    clickup_bind_ids = fields.One2many(
        "clickup.project.task.type",
        "odoo_id",
        string="Clickup Backend ID",
        readonly=True,
    )

    clickup_backend_id = fields.Many2one(
        "clickup.backend",
        related="clickup_bind_ids.backend_id",
        string="Clickup Backend",
        readonly=True,
    )


class TaskTypeAdapter(Component):
    _name = "clickup.project.task.type.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.project.task.type"
    _clickup_model = "/folder"
    _clickup_ext_id_key = "id"

    def search_read(self, filters=None):
        """
        Returns the information of a record

        :rtype: dict
        """
        data = []

        team_id = self.backend_record.team_id
        if team_id:
            self._clickup_model = "/team/{}/space".format(team_id)
            team_payload = self._call(self._clickup_model, arguments=filters)

            if team_payload:
                for rec in team_payload["spaces"]:
                    data.append(rec)
        return data
