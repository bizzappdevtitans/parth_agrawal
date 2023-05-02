from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ImportClickupWizard(models.TransientModel):
    _name = "import.clickup.project.wizard"
    _description = "import clickup projects through wizard"

    clickup_project_id = fields.Char(string="Clickup Project Id", required=True)
    clickup_api_key = fields.Char(String="Clickup Api Key", required=True)

    def get_clickup_payload(self):
        """This method return the clickup's project and task payload"""
        import requests

        list_id = self.clickup_project_id
        url = "https://api.clickup.com/api/v2/list/" + list_id

        headers = {"Authorization": self.clickup_api_key}

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise ValidationError(_("Invalid ClickUp project ID or API key"))

        data = response.json()

        # Get tasks information for the list
        tasks_url = "https://api.clickup.com/api/v2/list/{}/task".format(list_id)
        tasks_response = requests.get(tasks_url, headers=headers)
        tasks_data = tasks_response.json()

        # Add tasks information to the returned payload
        data["tasks"] = tasks_data["tasks"]

        return data

    def action_on_click_import(self):
        data = self.get_clickup_payload()
        external_id = data.get("id")

        # Check if project with same external ID already exists
        existing_project = self.env["project.project"].search(
            [("external_id", "=", external_id)], limit=1
        )

        if existing_project:
            # Update existing project
            existing_project.write(
                {
                    "name": data.get("name"),
                    "description": data.get("content"),
                }
            )
            imported_project = existing_project
        else:
            # Create new project
            imported_project = self.env["project.project"].create(
                {
                    "external_id": external_id,
                    "name": data.get("name"),
                    "description": data.get("content"),
                }
            )

        # Create or update tasks for the project
        task_obj = self.env["project.task"]
        stage_obj = self.env["project.task.type"]
        for task in data.get("tasks", []):
            task_external_id = task.get("id")
            task_status = task.get("status").get("status")

            # Check if task with same external ID already exists
            existing_task = task_obj.search(
                [("external_id", "=", task_external_id)], limit=1
            )

            # Check if stage with same name already exists
            existing_stage = stage_obj.search(
                [("name", "=", task_status), ("project_ids", "=", imported_project.id)],
                limit=1,
            )

            # Create new stage if it doesn't exist
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

            # Update existing task or create new task
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
