from odoo import _, fields, models

from odoo.addons.component.core import Component
from odoo.exceptions import UserError, ValidationError


class ClickupProjectProject(models.Model):
    _name = "clickup.project.project"
    _inherit = ["clickup.model"]
    _inherits = {"project.project": "odoo_id"}
    _description = "Clickup project.project binding model"

    odoo_id = fields.Many2one(
        "project.project", string="Project", required=True, ondelete="restrict"
    )
    synced_at = fields.Datetime(string="Synced At", readonly=True)


class ProjectProject(models.Model):
    _inherit = "project.project"
    _description = "Inherited project.project model"

    clickup_bind_ids = fields.One2many(
        "clickup.project.project",
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

    synced_at = fields.Datetime(
        string="Synced At", related="clickup_bind_ids.synced_at", readonly=True
    )

    folder_id = fields.Char(string="Folder Id", readonly=True)

    def get_clickup_project_payload(self):
        """This method returns the clickup's project and task payload"""
        import requests

        list_id = self.external_id
        url = "https://api.clickup.com/api/v2/list/" + list_id

        headers = {"Authorization": self.api_token_data}

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise ValidationError(
                _(
                    "Invalid API key to update the project,Please import project to update",
                )
            )

        data = response.json()

        tasks_url = "https://api.clickup.com/api/v2/list/{}/task".format(list_id)
        tasks_response = requests.get(tasks_url, headers=headers)
        tasks_data = tasks_response.json()

        data["tasks"] = tasks_data["tasks"]

        return data

    def open_project(self):
        data = self.get_clickup_project_payload()
        for task in data.get("tasks", []):
            team_id = task.get("team_id")

            result = {
                "type": "ir.actions.act_url",
                "url": f"https://app.clickup.com/{team_id}/v/l/li/{self.external_id}",
                "target": "new",
            }

            return result

    def update_project(self, job_options=None):
        pass

    def export_changes_to_clickup_project(self):
        self.ensure_one()
        if not self.backend_id:
            raise UserError(_("Please add backend!!!"))
        self.env["clickup.project.project"].export_record(
            backend=self.sudo().backend_id, record=self
        )

        for task in self.tasks:
            self.env["clickup.project.tasks"].export_record(
                backend=self.sudo().backend_id, record=task
            )


class ProjectAdapter(Component):
    _name = "clickup.project.project.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.project.project"
    _clickup_model = "/folder/{}/list"
    _odoo_ext_id_key = "external_id"
    _clickup_ext_id_key = "id"

    def search(self, filters=None):
        """
        Returns the information of a record

        :rtype: dict
        """
        if self.backend_record.test_mode is True:
            print("comming inside")
            backend_record = self.backend_record
            folder_id = (
                backend_record.test_location if backend_record.test_location else None
            )
            print("\n\n folder id", folder_id)
        else:
            print("production")
            backend_record = self.backend_record
            folder_id = backend_record.uri if backend_record.uri else None

        resource_path = "/folder/{}/list".format(folder_id)
        self._clickup_model = resource_path
        return super(ProjectAdapter, self).search(filters)

    def create(self, data):
        """
        Returns the information of a record

        :rtype: dict
        """
        if self.backend_record.test_mode is True:
            backend_record = self.backend_record
            folder_id = (
                backend_record.test_location if backend_record.test_location else None
            )
        else:
            backend_record = self.backend_record
            folder_id = backend_record.uri if backend_record.uri else None

        resource_path = "/folder/{}/list".format(folder_id)
        self._clickup_model = resource_path
        return super(ProjectAdapter, self).create(data)

    def write(self, external_id, data):
        """Update records on the external system"""
        if self.backend_record.test_mode is True:
            backend_record = self.backend_record
            folder_id = (
                backend_record.test_location if backend_record.test_location else None
            )
        else:
            backend_record = self.backend_record
            folder_id = backend_record.uri if backend_record.uri else None

        resource_path = "/folder/{}/list".format(folder_id)
        self._clickup_model = resource_path
        if external_id:
            resource_path = "/list/{}".format(external_id)
            self._clickup_model = resource_path
            return super(ProjectAdapter, self).write(external_id, data)
