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
        data = self.env["clickup.backend"]
        list_id = data.uri
        resource_path = "/list/" + list_id + "/task"
        result = self._call(resource_path, arguments=filters)
        return result

    # def _call(self, method, arguments, http_method=None, storeview=None):
    #     try:
    #         return super(ProjectAdapter, self)._call(
    #             method, arguments, http_method=http_method, storeview=storeview
    #         )
    #     except xmlrpc.client.Fault as err:
    #         # this is the error in the Magento API
    #         # when the customer does not exist
    #         if err.faultCode == 102:
    #             raise ProjectAdapter
    #         else:
    #             raise

    # def read(self, external_id, attributes=None, storeview=None):
    #     """Returns the information of a record"""
    #     return

    # def _call(self, method, arguments=None, http_method=None, storeview=None):
    #     search_json = arguments.get("search")
    #     search_dict = json.loads(search_json) if search_json else {}
    #     find = search_dict.get("updated", [{}])[0].get("action")

    #     if self._akeneo_model == "clickup.project.project":
    #         if find == "import":
    #             return super(ProjectAdapter, self)._call(
    #                 method, arguments, http_method="get", storeview=storeview
    #             )
    #         if find == "export":
    #             return super(ProjectAdapter, self)._call(
    #                 method, arguments, http_method="post", storeview=storeview
    #             )
