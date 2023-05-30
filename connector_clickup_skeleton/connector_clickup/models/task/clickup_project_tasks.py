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
    _akeneo_model = "clickup.project.tasks"
    _akeneo_ext_id_key = "id"

    def search(self, filters=None):
        """
        Returns the information of a record

        :rtype: dict
        """
        # self.env["clickup.backend"]
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

            resource_path = "/list/" + list_id + "/task"
            project_result = self._call(resource_path, arguments=filters)
            result.append(project_result)

        return result

    # def _call(self, method, arguments=None, http_method=None, storeview=None):
    #     search_json = arguments.get("search")
    #     search_dict = json.loads(search_json) if search_json else {}
    #     find = search_dict.get("updated", [{}])[0].get("action")

    #     if self._akeneo_model == "clickup.project.tasks":
    #         if find == "import":
    #             return super(TaskAdapter, self)._call(
    #                 method, arguments, http_method="get", storeview=storeview
    #             )
    #         if find == "export":
    #             return super(TaskAdapter, self)._call(
    #                 method, arguments, http_method="post", storeview=storeview
    #             )
