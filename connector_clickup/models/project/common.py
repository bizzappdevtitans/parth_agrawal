from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import ustr

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
    _description = "Inherited project.project model"

    clickup_bind_ids = fields.One2many(
        "clickup.project.project",
        "odoo_id",
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
        readonly=False,
        store=True,
    )

    folder_id = fields.Char(readonly=True)

    export_to_folder = fields.Boolean()

    folder_info = fields.Char()

    def action_open_project_in_clickup(self):
        """Open co-responding project in clickup's website"""
        result = {
            "type": "ir.actions.act_url",
            "url": f"https://app.clickup.com/{self.folder_id}/v/l/li/{self.external_id}",
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
            external_id=self.external_id,
        )

        for task in self.tasks:
            self.env["clickup.project.tasks"].import_record(
                backend=self.sudo().clickup_backend_id, external_id=task.external_id
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
            self.env["clickup.project.tasks"].export_record(
                backend=self.sudo().clickup_backend_id, record=task
            )

    def export_project_to_clickup(self):
        """Export newly created project from odoo to clickup website"""
        self.ensure_one()
        if not self.clickup_backend_id:
            raise UserError(_("Please add backend!!!"))
        try:
            self.env["clickup.project.project"].export_record(
                backend=self.sudo().clickup_backend_id, record=self
            )
        except Exception as ex:
            raise ValidationError from ex(ustr(ex))


class ProjectAdapter(Component):
    _name = "clickup.project.project.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.project.project"
    _clickup_model = "/list"
    _odoo_ext_id_key = "external_id"
    _clickup_ext_id_key = "id"

    def search_read(self, filters=None):
        """
        Returns the information of a record

        :rtype: dict
        """
        data = []

        space_id = self.backend_record.uri

        folder_resource_path = "/space/{}/folder".format(space_id)
        self._clickup_model = folder_resource_path
        folder_project_payload = self._call(folder_resource_path, arguments=filters)

        list_resource_path = "/space/{}/list".format(space_id)
        self._clickup_model = list_resource_path
        space_project_payload = self._call(list_resource_path, arguments=filters)

        if folder_project_payload:
            for rec in folder_project_payload["folders"]:
                for item in rec["lists"]:
                    data.append(item)
        if space_project_payload:
            for rec in space_project_payload["lists"]:
                data.append(rec)

        return data

    def create(self, data):
        """
        Returns the information of a record

        :rtype: dict
        """
        # if self.backend_record.test_mode is True:
        #     backend_record = self.backend_record
        #     folder_id = (
        #         backend_record.test_location if backend_record.test_location else None
        #     )
        # else:
        #     backend_record = self.backend_record
        #     folder_id = backend_record.uri if backend_record.uri else None
        space_id = self.backend_record.uri
        resource_path = "/space/{}/list".format(space_id)
        folder = data.get("folder")
        project = self.env["project.project"].search([("folder", "=", folder)])
        if project:
            resource_path = "/folder/{}/list".format(folder)
            self._clickup_model = resource_path

        self._clickup_model = resource_path
        return super().create(data)

    def write(self, external_id, data):
        """Update records on the external system"""
        # if self.backend_record.test_mode is True:
        #     backend_record = self.backend_record
        #     folder_id = (
        #         backend_record.test_location if backend_record.test_location else None
        #     )
        # else:
        #     backend_record = self.backend_record
        #     folder_id = backend_record.uri if backend_record.uri else None

        # resource_path = "/folder/{}/list".format(folder_id)
        # self._clickup_model = resource_path
        if external_id:
            resource_path = "/list/{}".format(external_id)
            self._clickup_model = resource_path
            return super().write(external_id, data)
