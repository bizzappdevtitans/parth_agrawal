import xmlrpc.client

from odoo import _, fields, models
import json
from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError, UserError


class ClickupProjectTasks(models.Model):
    _name = "clickup.project.tasks"
    _inherits = {"project.task": "odoo_id"}
    _inherit = ["clickup.model"]
    _description = "Clickup project.tasks binding model"

    odoo_id = fields.Many2one(
        "project.task", string="Task", required=True, ondelete="restrict"
    )
    created_at = fields.Datetime(string="Created At", readonly=True)

    updated_at = fields.Datetime(string="Updated At", readonly=True)


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

    created_at = fields.Datetime(
        string="Created At", related="clickup_bind_ids.created_at", readonly=True
    )

    updated_at = fields.Datetime(
        string="Updated At", related="clickup_bind_ids.updated_at", readonly=True
    )
    folder_id = fields.Char(string="Folder Id", readonly=True)

    def open_task(self):
        """This method open the particular task on clickup's website"""
        return {
            "type": "ir.actions.act_url",
            "url": f"https://app.clickup.com/t/{self.external_id}",
            "target": "new",
        }

    def update_task(self):
        pass

    def export_changes_to_clickup_task(self):
        self.ensure_one()
        if not self.backend_id:
            raise UserError(_("Please add backend!!!"))
        self.env["clickup.project.tasks"].export_record(
            backend=self.sudo().backend_id, record=self
        )


class TaskAdapter(Component):
    _name = "clickup.project.task.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.project.tasks"
    _clickup_model = "/list/{}/task"
    _clickup_ext_id_key = "id"

    def search(self, filters=None):
        """
        Returns the information of a record
        :rtype: dict
        """

        if self.backend_record.test_mode is True:
            print("test_mode")
            backend_record = self.backend_record
            folder_id = (
                backend_record.test_location if backend_record.test_location else None
            )
        else:
            print("production")
            backend_record = self.backend_record
            folder_id = backend_record.uri if backend_record.uri else None

        project_model = self.env["project.project"]

        projects = project_model.search([("folder_id", "=", folder_id)])
        result = []

        for project_record in projects:
            external_id = project_record.external_id
            if not external_id:
                continue

            list_id = external_id

            resource_path = "/list/{}/task".format(list_id)
            self._clickup_model = resource_path

            super_result = super(TaskAdapter, self).search(filters)
            result.append(super_result)

        return result

    def create(self, data):
        """
        Returns the information of a record

        :rtype: dict
        """

        external_id = data.get("project_id")
        if external_id:
            resource_path = "/list/{}/task".format(external_id)
            self._clickup_model = resource_path
            return super(TaskAdapter, self).create(data)

    def write(self, external_id, data):
        """Update records on the external system"""
        if external_id:
            resource_path = "/task/{}".format(external_id)
            self._clickup_model = resource_path
            return super(TaskAdapter, self).write(external_id, data)
