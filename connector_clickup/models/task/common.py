from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.component.core import Component


class ClickupProjectTasks(models.Model):
    _name = "clickup.project.tasks"
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
            "url": f"https://app.clickup.com/t/{self.external_id}",
            "target": "new",
        }

    def update_import_task(self):
        self.ensure_one()
        if not self.clickup_backend_id:
            raise UserError(_("Please add backend!!!"))
        self.env["clickup.project.tasks"].import_record(
            backend=self.sudo().clickup_backend_id,
            external_id=self.external_id,
        )

    def update_export_task(self):
        self.ensure_one()
        if not self.clickup_backend_id:
            raise UserError(_("Please add backend!!!"))
        self.env["clickup.project.tasks"].export_record(
            backend=self.sudo().clickup_backend_id, record=self
        )


class TaskAdapter(Component):
    _name = "clickup.project.task.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.project.tasks"
    _clickup_model = "/task"
    _clickup_ext_id_key = "id"
    _model_dependencies = [
        ("clickup.project.project", "id"),
    ]

    def search(self, filters=None, from_date=None, to_date=None):
        """
        Returns the information of a record
        :rtype: dict
        """

        # if self.backend_record.test_mode is True:
        #     print("test_mode")
        #     backend_record = self.backend_record
        #     folder_id = (
        #         backend_record.test_location if backend_record.test_location else None
        #     )
        # else:
        #     print("production")
        #     backend_record = self.backend_record
        #     folder_id = backend_record.uri if backend_record.uri else None

        data = []
        folder_ids = []
        list_ids = []

        space_ids = self.backend_record.uri.split(",")

        for space_id in space_ids:
            folder_resource_path = "/space/{}/folder".format(space_id)

            self._clickup_model = folder_resource_path
            folder_project_payload = self._call(folder_resource_path, arguments=filters)

            list_resource_path = "/space/{}/list".format(space_id)

            self._clickup_model = list_resource_path
            space_project_payload = self._call(list_resource_path, arguments=filters)

            if folder_project_payload:
                for record in folder_project_payload.get("folders", []):
                    items = record.get("id")
                    folder_ids.append(items)

            for folder_id in folder_ids:
                folder_path = "/folder/{}/list".format(folder_id)

                self._clickup_model = folder_path
                folder_payload = self._call(folder_path, arguments=filters)

                data.append(folder_payload)

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

            resource_path = "/list/{}/task".format(external_id)
            self._clickup_model = resource_path
            task_payload = self._call(resource_path, arguments=filters)
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
