from datetime import datetime, time

from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError


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
        """This method returns the clickup's task payload"""
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
        """This method update the tasks from clickup's task payload"""
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
        """This method open the particular task on clickup's website"""
        return {
            "type": "ir.actions.act_url",
            "url": f"https://app.clickup.com/t/{self.external_id}",
            "target": "new",
        }

    def export_changes_task_api(self, payload):
        """This method send the particular task's changes to clickup's website"""
        import requests

        task_id = self.external_id
        url = "https://api.clickup.com/api/v2/task/" + task_id

        query = {"custom_task_ids": "true", "team_id": "123"}

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_token_data,
        }

        response = requests.put(url, json=payload, headers=headers, params=query)

        response.json()

        if response.status_code == 200:
            raise UserError(
                _("The task changes have been updated in ClickUp successfully")
            )

    def export_changes_to_clickup_task(self):
        """This method send payload to export task changes to clickup's website"""

        if self.date_deadline:
            deadline_datetime = datetime.combine(self.date_deadline, time.min)
        else:
            deadline_datetime = None

        if deadline_datetime:
            unix_timestamp = int(deadline_datetime.timestamp())
        else:
            unix_timestamp = None

        payload = {
            "name": self.name,
            "description": self.description,
            "priority": 1,
            "due_date": unix_timestamp,
            "due_date_time": True,
            "parent": "abc1234",
            "time_estimate": 8640000,
            "start_date": 1567780450202,
            "start_date_time": False,
            "assignees": {"add": [], "rem": []},
            "archived": False,
        }

        self.export_changes_task_api(payload)

    def export_new_task_api(self, payload):
        """This method send the new task to clickup's website"""
        import requests

        list_id = self.project_id.external_id
        api_token_data = self.project_id.api_token_data

        url = "https://api.clickup.com/api/v2/list/" + list_id + "/task"

        query = {"custom_task_ids": "true", "team_id": "123"}

        headers = {
            "Content-Type": "application/json",
            "Authorization": api_token_data,
        }

        response = requests.post(url, json=payload, headers=headers, params=query)

        response.json()

        if response.status_code == 200:
            raise UserError(
                _("The task changes have been updated in ClickUp successfully")
            )

    def export_task_to_clickup_task(self):
        """This method send payload to export new task to clickup's website"""

        if self.date_deadline:
            deadline_datetime = datetime.combine(self.date_deadline, time.min)
        else:
            deadline_datetime = None

        if deadline_datetime:
            unix_timestamp = int(deadline_datetime.timestamp())
        else:
            unix_timestamp = None

        payload = {
            "name": self.name,
            "description": self.description,
            "assignees": [],
            "tags": [],
            "status": "",
            "priority": 3,
            "due_date": unix_timestamp,
            "due_date_time": False,
            "time_estimate": 8640000,
            "start_date": 1567780450202,
            "start_date_time": False,
            "notify_all": False,
            "parent": None,
            "links_to": None,
            "check_required_custom_fields": False,
        }

        self.export_new_task_api(payload)
