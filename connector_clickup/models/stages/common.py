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


class TaskTypeAdapter(Component):
    _name = "clickup.project.task.type.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.project.task.type"
    _clickup_model = "/list/{}/task"
    _clickup_ext_id_key = "status"

    def search(self, filters=None):
        """
        Returns the information of a record
        :rtype: dict
        """
        if self.backend_record.test_mode is True:
            print("\n\ntest_mode\n\n")
            backend_record = self.backend_record
            folder_id = (
                backend_record.test_location if backend_record.test_location else None
            )
        else:
            print("\n\nproduction\n\n")
            backend_record = self.backend_record
            folder_id = backend_record.uri if backend_record.uri else None

        project_model = self.env["project.project"]

        projects = project_model.search([("folder_id", "=", folder_id)])
        result = []

        for project_record in projects:
            external_id = project_record.external_id
            if not external_id:
                continue

            list_id = external_id

            resource_path = "/list/{}/task".format(list_id)
            self._clickup_model = resource_path
            # project_result = self._call(resource_path, arguments=filters)

            # result.append(resource_path)
            super_result = super(TaskTypeAdapter, self).search(filters)
            result.append(super_result)

        return result
