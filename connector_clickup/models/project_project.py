from datetime import datetime

from odoo import _, fields, models
from odoo.exceptions import ValidationError


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
    clickup_backend_id = fields.Many2one(
        "clickup.backend",
        related="clickup_bind_ids.clickup_backend_id",
        string="Clickup Backend",
        readonly=True,
    )

    api_token_data = fields.Char(
        string="API token",
        related="clickup_bind_ids.api_token_data",
        readonly=True,
    )

    created_at = fields.Datetime(
        string="Created At", related="clickup_bind_ids.created_at", readonly=True
    )

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

    def update_project(self):
        """This method update the clickup's project and task payload"""
        data = self.get_clickup_project_payload()
        external_id = data.get("id")

        existing_project = self.env["project.project"].search(
            [("external_id", "=", external_id)], limit=1
        )

        if existing_project:
            existing_project.write(
                {
                    "name": data.get("name"),
                    "api_token_data": self.api_token_data,
                    "description": data.get("content"),
                }
            )
            imported_project = existing_project

        task_obj = self.env["project.task"]
        stage_obj = self.env["project.task.type"]
        for task in data.get("tasks", []):
            task_external_id = task.get("id")
            task_status = task.get("status").get("status")

            clickup_timestamp = int(task.get("date_updated")) // 1000
            clickup_update = datetime.fromtimestamp(clickup_timestamp)
            name = task.get("name")
            task_model = self.env["project.task"].search([("name", "=", name)], limit=1)
            existing_task = task_obj.search(
                [
                    ("external_id", "=", task_external_id),
                ],
                limit=1,
            )

            existing_stage = stage_obj.search(
                [("name", "=", task_status)],
                limit=1,
            )

            if not existing_stage:
                existing_stage = self.env["clickup.project.task.type"].create(
                    {
                        "name": task_status,
                        "api_token_data": self.api_token_data,
                        "external_id": task_status,
                        "clickup_backend_id": self.id,
                    }
                )

            task_vals = {
                "name": task.get("name"),
                "description": task.get("text_content"),
                "stage_id": existing_stage.id,
                "api_token_data": self.api_token_data,
                "project_id": imported_project.id,
                "external_id": task_external_id,
                "user_id": self.env.user.id,
                "updated_at": datetime.now(),
            }

            task_vals_new = {
                "name": task.get("name"),
                "description": task.get("text_content"),
                "stage_id": existing_stage.id,
                "api_token_data": self.api_token_data,
                "project_id": imported_project.id,
                "external_id": task_external_id,
                "user_id": self.env.user.id,
                "created_at": datetime.now(),
            }

            if (
                existing_task.updated_at is False
                or existing_task.updated_at < clickup_update
            ):
                existing_task.write(task_vals)
            if not existing_task:
                self.env["clickup.project.tasks"].create(task_vals_new)
                if task_model:
                    if task_model and existing_task:
                        continue
                    else:
                        task_model.unlink()

        result = {
            "name": "Project",
            "view_mode": "form",
            "res_model": "project.project",
            "res_id": imported_project.id,
            "type": "ir.actions.act_window",
        }

        return result

    def open_clickup_project(self):
        """This method open the particular project on clickup's website"""
        data = self.get_clickup_project_payload()
        for task in data.get("tasks", []):
            team_id = task.get("team_id")
            return {
                "type": "ir.actions.act_url",
                "url": f"https://app.clickup.com/{team_id}/v/l/li/{self.external_id}",
                "target": "new",
            }

    def export_project_api(self, payload):
        """This method export the changes that heppened in project to clickup's website"""

        import requests

        list_id = self.external_id
        url = "https://api.clickup.com/api/v2/list/" + list_id

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_token_data,
        }

        response = requests.put(url, json=payload, headers=headers)

        response.json()

        old_tasks = self.env["project.task"].search(
            [("project_id", "=", self.id), ("external_id", "!=", False)]
        )

        for tasks in old_tasks:
            tasks.export_changes_to_clickup_task()

        new_tasks = self.env["project.task"].search([("project_id", "=", self.id)])

        for new_task in new_tasks:
            if not new_task.external_id and new_task.disable_button is False:
                new_task.export_task_to_clickup_task()
                new_task.disable_button = True

    def export_to_clickup_project(self):
        """Payload to export the changes that heppened in project to clickup's website"""

        payload = {
            "name": self.name,
            "content": self.description,
            "assignee": "none",
            "unset_status": True,
        }
        self.export_project_api(payload)

    def api_to_export_new_project(self, payload):
        """This method export the new project to clickup's website"""
        import requests

        # folder_id = "90020435594"
        # url = "https://api.clickup.com/api/v2/folder/" + folder_id + "/list"

        space_id = "90020155368"
        url = "https://api.clickup.com/api/v2/space/" + space_id + "/list"

        headers = {
            "Content-Type": "application/json",
            "Authorization": "pk_67222607_9TATNL43QDZ5M0KWHNLQPF41L3EFNQLM",
        }

        response = requests.post(url, json=payload, headers=headers)

        response.json()

    def export_project_to_clickup_project(self):
        """Payload which helps to export the new project to clickup's website"""

        payload = {
            "name": self.name,
            "content": self.description,
            "due_date": 1567780450202,
            "due_date_time": False,
            "priority": 1,
            "assignee": 183,
            "status": "red",
        }

        self.api_to_export_new_project(payload)
