from odoo import _, models, fields, api
from odoo.exceptions import ValidationError
from pprint import pprint


class ClickupBackend(models.Model):
    _name = "clickup.backend"

    api_key = fields.Char(string="API Key/Token", required=True)
    uri = fields.Char(string="URI/Location", required=True)

    def import_projects(self):
        import requests

        folder_id = self.uri
        url = "https://api.clickup.com/api/v2/folder/" + folder_id + "/list"

        headers = {"Authorization": self.api_key}

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise ValidationError(_("Invalid ClickUp project ID or API key"))

        data = response.json()
        pprint(data)

        for project in data["lists"]:
            existing_project = self.env["clickup.project.project"].search(
                [("external_id", "=", project.get("id"))]
            )
            if existing_project:
                existing_project.write({"name": project.get("name")})
            else:
                vals = {
                    "name": project.get("name"),
                    "external_id": project.get("id"),
                }
                self.env["clickup.project.project"].create(vals)

    def import_tasks(self):
        import requests

        folder_id = self.uri
        tasks_url = f"https://api.clickup.com/api/v2/folder/{folder_id}/tasks"
        headers = {"Authorization": self.api_key}

        tasks_response = requests.get(tasks_url, headers=headers)

        if tasks_response.status_code != 200:
            raise ValidationError(_("Invalid ClickUp folder ID or API key"))

        tasks_data = tasks_response.json()
        pprint(tasks_data)

        for task in tasks_data["tasks"]:
            project_id = task.get("list", {}).get("id")
            project = self.env["clickup.project.project"].search(
                [("external_id", "=", project_id)]
            )
            if project:
                task_name = task.get("name")
                task_desc = task.get("description")
                task_assignee_id = (
                    task.get("assignees", [])[0].get("id")
                    if task.get("assignees")
                    else False
                )
                task_due_date = task.get("due_date")
                task_status = task.get("status").get("status")

                vals = {
                    "name": task_name,
                    "description": task_desc,
                    "assignee_id": task_assignee_id,
                    "due_date": task_due_date,
                    "status": task_status,
                    "odoo_id": project.odoo_id.id,
                }
                self.env["clickup.project.tasks"].create(vals)

    def import_stages(self):
        pass


class ClickupProjectProject(models.Model):
    _name = "clickup.project.project"
    _inherits = {"project.project": "odoo_id"}
    _inherit = ["clickup.model"]

    odoo_id = fields.Many2one(
        "project.project", string="Project", required=True, ondelete="restrict"
    )


class ClickupProjectTasks(models.Model):
    _name = "clickup.project.tasks"
    _inherits = {"project.task": "odoo_id"}
    _inherit = ["clickup.model"]

    odoo_id = fields.Many2one(
        "project.task", string="Task", required=True, ondelete="restrict"
    )


class ClickupProjectTaskType(models.Model):
    _name = "clickup.project.task.type"
    _inherits = {"project.task.type": "odoo_id"}
    _inherit = ["clickup.model"]

    odoo_id = fields.Many2one(
        "project.task.type", string="Stage", required=True, ondelete="cascade"
    )
