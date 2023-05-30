from odoo import _, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class ClickupProjectProject(models.Model):
    _name = "clickup.project.project"
    _inherit = ["clickup.model"]
    _inherits = {"project.project": "odoo_id"}
    _description = "Clickup project.project binding model"

    odoo_id = fields.Many2one(
        "project.project", string="Project", required=True, ondelete="restrict"
    )


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

    api_token_data = fields.Char(
        related="clickup_bind_ids.api_token_data",
        string="API token",
        readonly=True,
    )

    created_at = fields.Datetime(string="Created At", readonly=True)

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


class ProjectAdapter(Component):
    _name = "clickup.project.project.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.project.project"
    _akeneo_model = "clickup.project.project"
    _odoo_ext_id_key = "external_id"
    _akeneo_ext_id_key = "id"

    def search(self, filters=None):
        """
        Returns the information of a record

        :rtype: dict
        """
        # self.env["clickup.backend"]
        backend_record = self.backend_record  # Retrieve the first record
        folder_id = backend_record.uri if backend_record.uri else None

        resource_path = "/folder/" + folder_id + "/list"
        result = self._call(resource_path, arguments=filters)
        return result

    # def search(self, filters=None):
    #     """
    #     Returns the information of a record

    #     :rtype: dict
    #     """
    #     backend_model = self.env["clickup.backend"]
    #     backend_record = self.backend_record  # Retrieve the first record
    #     folder_id = backend_record.uri if backend_record.uri else None
    #     print("folder_id==", folder_id)
    #     resource_path = "/folder/" + folder_id + "/list"
    #     self._akeneo_model = resource_path
    #     # result = self._call(resource_path, arguments=filters)
    #     return super(ProjectAdapter, self).search(filters)

    # def create(self, data):
    #     """Create a record on the external system"""
    #     print("\n\nWHAT IS DATA", data)
    #     backend_model = self.env["clickup.backend"]
    #     backend_record = self.backend_record  # Retrieve the first record
    #     folder_id = backend_record.uri if backend_record.uri else None
    #     print("folder_id==", folder_id)
    #     self._akeneo_model = "/folder/" + folder_id + "/list"
    #     # resource_path = self._akeneo_model
    #     # result = self._call(resource_path, data, http_method="post")
    #     return super(ProjectAdapter, self).create(data)


# import requests

# folder_id = "YOUR_folder_id_PARAMETER"
# url = "https://api.clickup.com/api/v2/folder/" + folder_id + "/list"

# query = {
#   "archived": "false"
# }

# headers = {"Authorization": "YOUR_API_KEY_HERE"}

# response = requests.get(url, headers=headers, params=query)

# data = response.json()
# print(data)

# import requests

# folder_id = "YOUR_folder_id_PARAMETER"
# url = "https://api.clickup.com/api/v2/folder/" + folder_id + "/list"

# payload = {
#   "name": "New List Name",
#   "content": "New List Content",
#   "due_date": 1567780450202,
#   "due_date_time": False,
#   "priority": 1,
#   "assignee": 183,
#   "status": "red"
# }

# headers = {
#   "Content-Type": "application/json",
#   "Authorization": "YOUR_API_KEY_HERE"
# }

# response = requests.post(url, json=payload, headers=headers)

# data = response.json()
# print(data)
