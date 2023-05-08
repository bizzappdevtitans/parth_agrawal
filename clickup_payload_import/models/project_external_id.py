from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ProjectExternalId(models.Model):
    _inherit = "project.project"
    _description = "inherited project model"

    external_id = fields.Char(string="External Id", readonly=True)
    api_token = fields.Char(string="API token", readonly=True)

    def get_clickup_project_payload(self):
        """This method returns the clickup's project and task payload"""
        import requests

        list_id = self.external_id
        url = "https://api.clickup.com/api/v2/list/" + list_id

        headers = {"Authorization": self.api_token}

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise ValidationError(
                _(
                    "Invalid API key to update the project,Please enter a valid API key manually in the Import Clickup Project Wizard",
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

        existing_project = self.search([("external_id", "=", external_id)], limit=1)

        if existing_project:
            existing_project.write(
                {
                    "name": data.get("name"),
                    "api_token": self.api_token,
                    "description": data.get("content"),
                }
            )
            imported_project = existing_project

        task_obj = self.env["project.task"]
        stage_obj = self.env["project.task.type"]
        for task in data.get("tasks", []):
            task_external_id = task.get("id")
            task_status = task.get("status").get("status")

            existing_task = task_obj.search(
                [("external_id", "=", task_external_id)], limit=1
            )

            existing_stage = stage_obj.search(
                [("name", "=", task_status), ("project_ids", "=", imported_project.id)],
                limit=1,
            )

            if not existing_stage:
                existing_stage = stage_obj.create(
                    {
                        "name": task_status,
                        "project_ids": [(4, imported_project.id)],
                    }
                )

            task_vals = {
                "name": task.get("name"),
                "description": task.get("text_content"),
                "stage_id": existing_stage.id,
                "project_id": imported_project.id,
                "external_id": task_external_id,
                "user_id": self.env.user.id,
            }

            if existing_task:
                existing_task.write(task_vals)
            else:
                task_obj.create(task_vals)

        result = {
            "name": "Project",
            "view_mode": "form",
            "res_model": "project.project",
            "res_id": imported_project.id,
            "type": "ir.actions.act_window",
        }

        return result
