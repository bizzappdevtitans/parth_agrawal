from datetime import datetime

import requests

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ClickupBackend(models.Model):
    _name = "clickup.backend"
    _description = "Clickup backend model"

    name = fields.Char(string="Clickup Backend ID", required=True)
    api_key = fields.Char(string="API Key/Token", required=True)
    uri = fields.Char(string="URI/Location", required=True)

    clickup_project_id = fields.Char(string="Clickup Project Id")

    def get_clickup_project_payload(self):
        """This method return the clickup's particular project and it's tasks payload"""

        list_id = self.clickup_project_id
        url = "https://api.clickup.com/api/v2/list/" + list_id

        headers = {"Authorization": self.api_key}

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise ValidationError(_("Invalid ClickUp project ID or API key"))

        data = response.json()

        tasks_url = "https://api.clickup.com/api/v2/list/{}/task".format(list_id)
        tasks_response = requests.get(tasks_url, headers=headers)
        tasks_data = tasks_response.json()

        data["tasks"] = tasks_data["tasks"]

        return data

    def get_clickup_projects_payload(self):
        """This method return the clickup's all projects payload"""

        folder_id = self.uri
        url = "https://api.clickup.com/api/v2/folder/" + folder_id + "/list"

        query = {"archived": "false"}

        headers = {"Authorization": self.api_key}

        response = requests.get(url, headers=headers, params=query)

        if response.status_code != 200:
            raise ValidationError(_("Invalid ClickUp folder ID or API key"))

        data = response.json()
        return data

    def import_projects(self):
        """This method takes clickup payload to import all the projects"""
        projects_data = self.get_clickup_projects_payload()
        for project in projects_data["lists"]:
            self.clickup_project_id = project["id"]
            project_data = self.get_clickup_project_payload()
            external_id = project_data.get("id")
            existing_project = self.env["clickup.project.project"].search(
                [("external_id", "=", external_id)], limit=1
            )
            if existing_project:
                existing_project.write(
                    {
                        "name": project_data.get("name"),
                        "description": project_data.get("content"),
                        "api_token_data": self.api_key,
                        "clickup_backend_id": self.id,
                    }
                )

            else:
                self.env["clickup.project.project"].create(
                    {
                        "external_id": external_id,
                        "api_token_data": self.api_key,
                        "clickup_backend_id": self.id,
                        "name": project_data.get("name"),
                        "description": project_data.get("content"),
                        "created_at": datetime.now(),
                    }
                )

    def import_tasks(self):
        """This method takes clickup payload to import all the project's Tasks"""
        projects_data = self.get_clickup_projects_payload()
        imported_projects = []

        for project in projects_data["lists"]:
            self.clickup_project_id = project["id"]
            project_data = self.get_clickup_project_payload()
            external_id = project_data.get("id")

            existing_project = self.env["project.project"].search(
                [("external_id", "=", external_id)], limit=1
            )
            if not existing_project:
                raise ValidationError(
                    _("You are trying to import tasks before importing project")
                )

            stage_obj = self.env["project.task.type"]
            task_obj = self.env["clickup.project.tasks"]

            for task in project_data.get("tasks", []):
                task_external_id = task.get("id")
                task_status = task.get("status").get("status")

                existing_task = task_obj.search(
                    [("external_id", "=", task_external_id)], limit=1
                )

                existing_stage = stage_obj.search(
                    [
                        ("external_id", "=", task_status),
                    ],
                    limit=1,
                )
                if not existing_stage:
                    raise ValidationError(
                        _("You are trying to import tasks before importing Stages")
                    )

                task_vals = {
                    "name": task.get("name"),
                    "api_token_data": self.api_key,
                    "description": task.get("text_content"),
                    "project_id": existing_project.id,
                    "stage_id": existing_stage.id,
                    "external_id": task_external_id,
                    "clickup_backend_id": self.id,
                    "user_id": self.env.user.id,
                }

                task_vals_new = {
                    "name": task.get("name"),
                    "api_token_data": self.api_key,
                    "description": task.get("text_content"),
                    "project_id": existing_project.id,
                    "stage_id": existing_stage.id,
                    "external_id": task_external_id,
                    "clickup_backend_id": self.id,
                    "user_id": self.env.user.id,
                    "created_at": datetime.now(),
                }

                if not existing_task:
                    task_obj.create(task_vals_new)

                else:
                    existing_task.write(task_vals)

            imported_projects.append(existing_project.id)

    def import_stages(self):
        """This method takes clickup payload to import all the stages for the tasks"""
        projects_data = self.get_clickup_projects_payload()

        for project in projects_data["lists"]:
            self.clickup_project_id = project["id"]
            project_data = self.get_clickup_project_payload()
            external_id = project_data.get("id")

            existing_project = self.env["clickup.project.project"].search(
                [("external_id", "=", external_id)], limit=1
            )
            if not existing_project:
                raise ValidationError(
                    _("You are trying to import stages before importing project")
                )

            stage_obj = self.env["clickup.project.task.type"]
            for task in project_data.get("tasks", []):
                task_status = task.get("status").get("status")

                existing_stage = stage_obj.search(
                    [
                        ("external_id", "=", task_status),
                    ],
                    limit=1,
                )

                if not existing_stage:
                    existing_stage = stage_obj.create(
                        {
                            "name": task_status,
                            "api_token_data": self.api_key,
                            "external_id": task_status,
                            "clickup_backend_id": self.id,
                        }
                    )
                else:
                    existing_stage = stage_obj.write(
                        {
                            "name": task_status,
                            "api_token_data": self.api_key,
                            "external_id": task_status,
                            "clickup_backend_id": self.id,
                        }
                    )
