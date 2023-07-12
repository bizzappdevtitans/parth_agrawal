from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.component.core import Component


class ClickupProjectTasks(models.Model):
    _name = "clickup.project.task"
    _inherits = {"project.task": "odoo_id"}
    _inherit = ["clickup.binding"]
    _description = "Clickup project.tasks binding model"

    odoo_id = fields.Many2one(
        "project.task", string="Task", required=True, ondelete="restrict"
    )
    created_at = fields.Datetime(readonly=True)

    updated_at = fields.Datetime(readonly=True)


class ProjectTask(models.Model):
    _inherit = "project.task"
    _description = "Inherited project.task model"

    clickup_bind_ids = fields.One2many(
        "clickup.project.task",
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
        related="clickup_bind_ids.backend_id",
        string="Clickup Backend",
        readonly=True,
    )

    created_at = fields.Datetime(related="clickup_bind_ids.created_at", readonly=True)

    updated_at = fields.Datetime(related="clickup_bind_ids.updated_at", readonly=True)
    project_info = fields.Char(readonly=True)

    def action_open_task_in_clickup(self):
        """This method open the particular task on clickup's website"""
        return {
            "type": "ir.actions.act_url",
            "url": f"https://app.clickup.com/t/{self.clickup_bind_ids.external_id}",
            "target": "new",
        }

    def update_import_task(self):
        """Update task from Clickup website to odoo"""
        self.ensure_one()
        if not self.clickup_backend_id:
            raise UserError(_("Please add backend!!!"))
        self.env["clickup.project.task"].import_record(
            backend=self.sudo().clickup_backend_id,
            external_id=self.clickup_bind_ids.external_id,
        )

    def update_export_task(self):
        """Update task from odoo to Clickup website"""
        self.ensure_one()
        if not self.clickup_backend_id:
            raise UserError(_("Please add backend!!!"))
        self.env["clickup.project.task"].export_record(
            backend=self.sudo().clickup_backend_id, record=self
        )


class TaskAdapter(Component):
    _name = "clickup.project.task.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.project.task"
    _clickup_model = "/task"
    _clickup_ext_id_key = "id"

    def search(self, filters=None, from_date=None, to_date=None):
        """
        Returns the information of a record
        :rtype: dict
        """

        data = []
        list_ids = []

        if self.backend_record.test_mode:
            space_ids = (
                self.backend_record.test_location.split(",")
                if self.backend_record.test_location
                else []
            )
        else:
            space_ids = (
                self.backend_record.uri.split(",") if self.backend_record.uri else []
            )

        folder_ids = []
        for space_id in space_ids:
            self._clickup_model = "/space/{}/folder".format(space_id)

            folder_project_payload = self._call(self._clickup_model, arguments=filters)
            if folder_project_payload:
                for record in folder_project_payload.get("folders", []):
                    items = record.get("id")
                    folder_ids.append(items)

            for folder_id in folder_ids:
                self._clickup_model = "/folder/{}/list".format(folder_id)
                folder_payload = self._call(self._clickup_model, arguments=filters)

                data.append(folder_payload)

            self._clickup_model = "/space/{}/list".format(space_id)
            space_project_payload = self._call(self._clickup_model, arguments=filters)
            if space_project_payload:
                data.append(space_project_payload)

            for rec in data:
                for data in rec.get("lists", []):
                    external_id = data.get("id")
                    list_ids.append(external_id)

        result = []
        for external_id in list_ids:
            if from_date is not None:
                filters["date_updated_gt"] = from_date

            if to_date is not None:
                filters["date_updated_lt"] = to_date

            self._clickup_model = "/list/{}/task".format(external_id)
            task_payload = self._call(self._clickup_model, arguments=filters)
            result.append(task_payload)

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
            return super().create(data)

    def write(self, external_id, data):
        """Update records on the external system"""
        if external_id:
            resource_path = "/task/{}".format(external_id)
            self._clickup_model = resource_path
            return super().write(external_id, data)
