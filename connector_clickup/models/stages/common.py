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
        related="clickup_bind_ids.backend_id",
        string="Clickup Backend",
        readonly=True,
    )


class TaskTypeAdapter(Component):
    _name = "clickup.project.task.type.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.project.task.type"
    _clickup_model = "/space/{}/folder"
    _clickup_ext_id_key = "id"

    def search_read(self, filters=None):
        """
        Returns the information of a record

        :rtype: dict
        """
        data = []

        space_id = self.backend_record.uri

        folder_resource_path = "/space/{}/folder".format(space_id)
        self._clickup_model = folder_resource_path
        folder_project_payload = self._call(folder_resource_path, arguments=filters)

        list_resource_path = "/space/{}/list".format(space_id)
        self._clickup_model = list_resource_path
        space_project_payload = self._call(list_resource_path, arguments=filters)

        if folder_project_payload:
            for rec in folder_project_payload["folders"]:
                for item in rec["lists"]:
                    data.append(item)
        if space_project_payload:
            for rec in space_project_payload["lists"]:
                data.append(rec)

        return data
