from odoo import fields, models

from odoo.addons.component.core import Component


class ClickupProjectTasks(models.Model):
    _name = "clickup.project.tasks"
    _inherits = {"project.task": "odoo_id"}
    _inherit = ["clickup.model"]
    _description = "Clickup project.tasks binding model"

    odoo_id = fields.Many2one(
        "project.task", string="Task", required=True, ondelete="restrict"
    )


class ProjectTask(models.Model):
    _inherit = "project.task"
    _description = "Inherited project.task model"

    clickup_bind_ids = fields.One2many(
        "clickup.project.tasks",
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
        related="clickup_bind_ids.api_token_data",
        string="API token",
        readonly=True,
    )
    created_at = fields.Datetime(string="Created At", readonly=True)

    updated_at = fields.Datetime(string="Updated At", readonly=True)
    folder_id = fields.Char(string="Folder Id", readonly=True)
    disable_button = fields.Boolean(default=False, readonly=False)

    def open_task(self):
        """This method open the particular task on clickup's website"""
        return {
            "type": "ir.actions.act_url",
            "url": f"https://app.clickup.com/t/{self.external_id}",
            "target": "new",
        }


class TaskAdapter(Component):
    _name = "clickup.project.task.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.project.tasks"
    _akeneo_model = "/list/{}/task"
    _akeneo_ext_id_key = "id"

    def search(self, filters=None):
        """
        Returns the information of a record
        :rtype: dict
        """

        backend_record = self.backend_record  # Retrieve the first record
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
            self._akeneo_model = resource_path

            super_result = super(TaskAdapter, self).search(filters)
            result.append(super_result)

        return result

    def create(self, data):
        """
        Returns the information of a record

        :rtype: dict
        """
        backend_record = self.backend_record  # Retrieve the first record
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
            self._akeneo_model = resource_path

            super_result = super(TaskAdapter, self).create(data)
            result.append(super_result)

            return result

    def write(self, external_id, data):
        """Update records on the external system"""
        backend_record = self.backend_record  # Retrieve the first record
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
            self._akeneo_model = resource_path
            if external_id:
                resource_path = "/task/{}".format(external_id)
                super_result = super(TaskAdapter, self).write(external_id, data)
            result.append(super_result)

        return result
