from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.component.core import Component


class ClickupProjectProject(models.Model):
    _name = "clickup.project.project"
    _inherit = ["clickup.binding"]
    _inherits = {"project.project": "odoo_id"}
    _description = "Clickup project.project binding model"

    odoo_id = fields.Many2one("project.project", required=True, ondelete="restrict")
    synced_at = fields.Datetime(readonly=True)


class ProjectProject(models.Model):
    _inherit = "project.project"

    clickup_bind_ids = fields.One2many(
        "clickup.project.project",
        "odoo_id",
        readonly=True,
    )

    clickup_backend_id = fields.Many2one(
        "clickup.backend",
        related="clickup_bind_ids.backend_id",
        string="Clickup Backend",
        readonly=False,
    )

    team_id = fields.Char(readonly=True)
    folder_id = fields.Char(readonly=True)

    export_to_folder = fields.Boolean()

    folder_info = fields.Selection(selection="_get_folder_options", readonly=False)

    def _get_folder_options(self):
        """Get available folders list to export project to particular folder"""
        folder_model = self.env["project.project"]
        folder_records = folder_model.search([])

        unique_folders = list({record.folder_id for record in folder_records})
        return [(folder_id, folder_id) for folder_id in unique_folders]

    def action_open_project_in_clickup(self):
        """Open co-responding project in clickup's website"""
        result = {
            "type": "ir.actions.act_url",
            "url": f"""https://app.clickup.com/{self.team_id}/v/l/li/
            {self.clickup_bind_ids.external_id}""",
            "target": "new",
        }

        return result

    def update_import_project(self):
        """Update co-responding project and it's tasks from clickup website to odoo"""
        self.ensure_one()
        if not self.clickup_backend_id:
            raise UserError(_("Please add backend!!!"))
        self.env["clickup.project.project"].import_record(
            backend=self.sudo().clickup_backend_id,
            external_id=self.clickup_bind_ids.external_id,
        )

        for task in self.tasks:
            self.env["clickup.project.task"].import_record(
                backend=self.sudo().clickup_backend_id,
                external_id=task.clickup_bind_ids.external_id,
            )

    def update_export_project(self):
        """Update co-responding project and it's tasks from odoo to clickup website"""
        self.ensure_one()
        if not self.clickup_backend_id:
            raise UserError(_("Please add backend!!!"))
        self.env["clickup.project.project"].export_record(
            backend=self.sudo().clickup_backend_id, record=self
        )

        for task in self.tasks:
            self.env["clickup.project.task"].export_record(
                backend=self.sudo().clickup_backend_id, record=task
            )

    def export_project_to_clickup(self):
        """Export newly created project and it's tasks from odoo to clickup website"""
        self.ensure_one()

        if not self.clickup_backend_id and not self.company_id.clickup_backend_id:
            raise UserError(_("Please add backend!!!"))
        try:
            self.env["clickup.project.project"].export_record(
                backend=self.sudo().company_id.clickup_backend_id, record=self
            )
            for task in self.tasks:
                self.env["clickup.project.task"].export_record(
                    backend=self.sudo().company_id.clickup_backend_id, record=task
                )
        except Exception as err:
            raise UserError from err()


class ProjectAdapter(Component):
    _name = "clickup.project.project.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.project.project"
    _clickup_model = "/list"
    _odoo_ext_id_key = "external_id"
    _clickup_ext_id_key = "id"

    def search(self, filters=None):
        """
        Returns the information of a record
        :rtype: dict
        """
        data = []
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

        return data

    def create(self, data):
        """
        Returns the information of a record

        :rtype: dict
        """

        if self.backend_record.test_mode is True:
            backend_record = self.backend_record
            space_id = (
                backend_record.test_location if backend_record.test_location else []
            )
        else:
            backend_record = self.backend_record
            space_id = backend_record.uri if backend_record.uri else []

        folder = data.get("folder")
        if folder:
            resource_path = "/folder/{}/list".format(folder)
            self._clickup_model = resource_path
        else:
            resource_path = "/space/{}/list".format(space_id)
            self._clickup_model = resource_path
        return super().create(data)

    def write(self, external_id, data):
        """Update records on the external system"""

        if external_id:
            resource_path = "/list/{}".format(external_id)
            self._clickup_model = resource_path
            return super().write(external_id, data)
