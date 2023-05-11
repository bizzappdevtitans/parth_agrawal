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

            existing_task = task_obj.search(
                [("external_id", "=", task_external_id)], limit=1
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
                or existing_task
                or existing_task.updated_at < clickup_update
            ):
                if existing_task:
                    existing_task.write(task_vals)
                elif not existing_task:
                    self.env["clickup.project.tasks"].create(task_vals_new)

                else:
                    raise ValidationError(
                        _(
                            "All the tasks of this Project is upto date",
                        )
                    )

        result = {
            "name": "Project",
            "view_mode": "form",
            "res_model": "project.project",
            "res_id": imported_project.id,
            "type": "ir.actions.act_window",
        }

        return result

    def open_clickup_project(self):
        data = self.get_clickup_project_payload()
        for task in data.get("tasks", []):
            team_id = task.get("team_id")
            return {
                "type": "ir.actions.act_url",
                "url": f"https://app.clickup.com/{team_id}/v/l/li/{self.external_id}",
                "target": "new",
            }


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

    updated_at = fields.Datetime(string="Updated At", readonly=True)

    def get_clickup_task_payload(self):
        """This method returns the clickup's project and task payload"""
        import requests

        task_id = self.external_id
        url = "https://api.clickup.com/api/v2/task/" + task_id

        query = {
            "custom_task_ids": "true",
            "team_id": "123",
            "include_subtasks": "true",
        }

        headers = {"Authorization": self.api_token_data}

        response = requests.get(url, headers=headers, params=query)

        if response.status_code != 200:
            raise ValidationError(
                _(
                    "Invalid API key to update the task,Please import task to update",
                )
            )

        data = response.json()

        return data

    def update_task(self):
        """This method update the clickup's project and task payload"""
        data = self.get_clickup_task_payload()

        task_obj = self.env["project.task"]
        stage_obj = self.env["project.task.type"]

        task_external_id = data.get("id")
        task_status = data.get("status").get("status")

        existing_task = task_obj.search(
            [("external_id", "=", task_external_id)], limit=1
        )

        existing_stage = stage_obj.search(
            [("name", "=", task_status)],
            limit=1,
        )

        if not existing_stage:
            self.env["clickup.project.task.type"].create(
                {
                    "name": task_status,
                    "api_token_data": self.api_token_data,
                    "external_id": task_status,
                }
            )

        task_vals = {
            "name": data.get("name"),
            "description": data.get("text_content"),
            "stage_id": existing_stage.id,
            "api_token_data": self.api_token_data,
            "external_id": task_external_id,
            "user_id": self.env.user.id,
            "updated_at": datetime.now(),
        }
        clickup_timestamp = int(data.get("date_updated")) // 1000
        clickup_update = datetime.fromtimestamp(clickup_timestamp)

        if self.updated_at is False or self.updated_at < clickup_update:
            existing_task.write(task_vals)

        else:
            raise ValidationError(
                _("Task has been updated since the last ClickUp update.")
            )

    def open_clickup_task(self):
        return {
            "type": "ir.actions.act_url",
            "url": f"https://app.clickup.com/t/{self.external_id}",
            "target": "new",
        }


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"
    _description = "Inherited project.task.type model"

    clickup_bind_ids = fields.One2many(
        "clickup.project.task.type",
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
