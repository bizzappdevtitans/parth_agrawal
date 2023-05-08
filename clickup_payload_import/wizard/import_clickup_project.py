from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ImportClickupWizard(models.TransientModel):
    _name = "import.clickup.project.wizard"
    _description = "import clickup projects through wizard"

    clickup_project_id = fields.Char(string="Clickup Project Id")
    clickup_folder_id = fields.Char(string="Clickup Folder Id")
    clickup_api_key = fields.Char(string="Clickup Api Token", required=True)
    clickup_import_type = fields.Selection(
        [
            ("importproject", "Import Particular Project"),
            ("importprojects", "Import All Projects"),
        ],
        string="Select Import Type",
        required=True,
        default="importproject",
    )

    def get_clickup_project_payload(self):
        """This method return the clickup's project and task payload"""
        import requests

        list_id = self.clickup_project_id
        url = "https://api.clickup.com/api/v2/list/" + list_id

        headers = {"Authorization": self.clickup_api_key}

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise ValidationError(_("Invalid ClickUp project ID or API key"))

        data = response.json()

        tasks_url = "https://api.clickup.com/api/v2/list/{}/task".format(list_id)
        tasks_response = requests.get(tasks_url, headers=headers)
        tasks_data = tasks_response.json()

        data["tasks"] = tasks_data["tasks"]

        return data

    def action_on_click_import_project(self):
        """This method takes clickup payload to import particular project and it's tasks"""
        data = self.get_clickup_project_payload()
        external_id = data.get("id")

        existing_project = self.env["project.project"].search(
            [("external_id", "=", external_id)], limit=1
        )

        if existing_project:
            existing_project.write(
                {
                    "name": data.get("name"),
                    "api_token": self.clickup_api_key,
                    "description": data.get("content"),
                }
            )
            imported_project = existing_project
        else:
            imported_project = self.env["project.project"].create(
                {
                    "external_id": external_id,
                    "api_token": self.clickup_api_key,
                    "name": data.get("name"),
                    "description": data.get("content"),
                }
            )

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

    def get_clickup_projects_payload(self):
        """This method return the clickup's all projects and tasks payload"""
        import requests

        folder_id = self.clickup_folder_id
        url = "https://api.clickup.com/api/v2/folder/" + folder_id + "/list"

        query = {"archived": "false"}

        headers = {"Authorization": self.clickup_api_key}

        response = requests.get(url, headers=headers, params=query)

        if response.status_code != 200:
            raise ValidationError(_("Invalid ClickUp folder ID or API key"))

        data = response.json()
        return data

    def action_on_click_import_projects(self):
        """This method takes clickup payload to import all the projects and it's tasks"""
        projects_data = self.get_clickup_projects_payload()
        imported_projects = []

        for project in projects_data["lists"]:
            self.clickup_project_id = project["id"]
            project_data = self.get_clickup_project_payload()
            external_id = project_data.get("id")

            existing_project = self.env["project.project"].search(
                [("external_id", "=", external_id)], limit=1
            )

            if existing_project:
                existing_project.write(
                    {
                        "name": project_data.get("name"),
                        "api_token": self.clickup_api_key,
                        "description": project_data.get("content"),
                    }
                )
                imported_project = existing_project
            else:
                imported_project = self.env["project.project"].create(
                    {
                        "external_id": external_id,
                        "api_token": self.clickup_api_key,
                        "name": project_data.get("name"),
                        "description": project_data.get("content"),
                    }
                )

            task_obj = self.env["project.task"]
            stage_obj = self.env["project.task.type"]
            for task in project_data.get("tasks", []):
                task_external_id = task.get("id")
                task_status = task.get("status").get("status")

                existing_task = task_obj.search(
                    [("external_id", "=", task_external_id)], limit=1
                )

                existing_stage = stage_obj.search(
                    [
                        ("name", "=", task_status),
                        ("project_ids", "=", imported_project.id),
                    ],
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

            imported_projects.append(imported_project.id)

        result = {
            "name": "Projects",
            "view_mode": "kanban,tree,form",
            "res_model": "project.project",
            "domain": [("id", "in", imported_projects)],
            "type": "ir.actions.act_window",
        }

        return result
