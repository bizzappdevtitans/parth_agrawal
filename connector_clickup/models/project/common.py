from odoo import _, fields, models
from odoo.tools.misc import ustr
from odoo.addons.component.core import Component
from odoo.exceptions import UserError, ValidationError


class ClickupProjectProject(models.Model):
    _name = "clickup.project.project"
    _inherit = ["clickup.model"]
    _inherits = {"project.project": "odoo_id"}
    _description = "Clickup project.project binding model"

    odoo_id = fields.Many2one(
        "project.project", string="Project", required=True, ondelete="restrict"
    )
    synced_at = fields.Datetime(string="Synced At", readonly=True)


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
    backend_id = fields.Many2one(
        "clickup.backend",
        related="clickup_bind_ids.backend_id",
        string="Clickup Backend",
        readonly=False,
        store=True,
    )

    synced_at = fields.Datetime(
        string="Synced At", related="clickup_bind_ids.synced_at", readonly=True
    )

    folder_id = fields.Char(string="Folder Id", readonly=True)

    export_to_folder = fields.Boolean(string="Export To Folder")

    folder = fields.Char(string="Enter Folder Id")

    def open_project(self):
        result = {
            "type": "ir.actions.act_url",
            "url": f"https://app.clickup.com/{self.folder_id}/v/l/li/{self.external_id}",
            "target": "new",
        }

        return result

    # self, backend, external_id, force=False, data=None, **kwargs

    def import_changes_from_clickup_project(self, job_options=None):
        self.ensure_one()
        if not self.backend_id:
            raise UserError(_("Please add backend!!!"))
        self.env["clickup.project.project"].import_record(
            backend=self.sudo().backend_id,
            external_id=self.external_id,
        )

        # for task in self.tasks:
        #     self.env["clickup.project.tasks"].import_record(
        #         backend=self.sudo().backend_id, record=task
        #     )

    def export_changes_to_clickup_project(self):
        self.ensure_one()
        if not self.backend_id:
            raise UserError(_("Please add backend!!!"))
        self.env["clickup.project.project"].export_record(
            backend=self.sudo().backend_id, record=self
        )

        for task in self.tasks:
            self.env["clickup.project.tasks"].export_record(
                backend=self.sudo().backend_id, record=task
            )

    def export_to_clickup(self):
        self.ensure_one()
        if not self.backend_id:
            raise UserError(_("Please add backend!!!"))
        try:
            self.env["clickup.project.project"].export_record(
                backend=self.sudo().backend_id, record=self
            )
        except Exception as ex:
            raise ValidationError(ustr(ex))


class ProjectAdapter(Component):
    _name = "clickup.project.project.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.project.project"
    # _clickup_model = "/folder/{}/list"
    # _clickup_model = "/team"
    _clickup_model = "/list"
    _odoo_ext_id_key = "external_id"
    _clickup_ext_id_key = "id"

    # def search(self, filters=None):
    #     """
    #     Returns the information of a record

    #     :rtype: dict
    #     """
    #     # if self.backend_record.test_mode is True:
    #     #     print("comming inside")
    #     #     backend_record = self.backend_record
    #     #     folder_id = (
    #     #         backend_record.test_location if backend_record.test_location else None
    #     #     )
    #     #     print("\n\n folder id", folder_id)
    #     # else:
    #     #     print("production")
    #     #     backend_record = self.backend_record
    #     #     folder_id = backend_record.uri if backend_record.uri else None
    #     space_id = self.backend_record.uri
    #     resource_path = "/space/{}/folder".format(space_id)
    #     # if not filters.get("folder_id"):
    #     #     resource_path = "/space/{}/list".format(space_id)
    #     # records = self.search(filters)
    #     # print("payload inside search", records)
    #     self._clickup_model = resource_path
    #     return super(ProjectAdapter, self).search(filters)

    # def search(self, filters=None):
    #     """
    #     Returns the information of a record

    #     :rtype: dict
    #     """
    #     print("new filter in search", filters)
    #     space_id = self.backend_record.uri
    #     print("\n\nbackend record\n\n", self.backend_record)

    #     list_resource_path = "/space/{}/list".format(space_id)
    #     self._clickup_model = list_resource_path
    #     list_results = super(ProjectAdapter, self).search(filters)

    #     folder_resource_path = "/space/{}/folder".format(space_id)
    #     self._clickup_model = folder_resource_path
    #     folder_results = super(ProjectAdapter, self).search(filters)

    #     # particular_resource_path = "/list/{}".format(space_id)
    #     # self._clickup_model = particular_resource_path
    #     # particular_result = super(ProjectAdapter, self).search(filters)

    #     data = []
    #     if folder_results:
    #         for rec in folder_results["folders"]:
    #             for item in rec["lists"]:
    #                 data.append(item)
    #     if list_results:
    #         for rec in list_results["lists"]:
    #             data.append(rec)

    #     return data

    #     # result = self._call(resource_path, arguments=filters)
    #     # filters.update({"entity": entity})
    #     # return result

    def search_read(self, filters=None):
        """
        Returns the information of a record

        :rtype: dict
        """
        print("new filter in search", filters)
        space_id = self.backend_record.uri
        print("\n\nbackend record\n\n", self.backend_record)

        list_resource_path = "/space/{}/list".format(space_id)
        self._clickup_model = list_resource_path
        result_1 = self._call(list_resource_path, arguments=filters)

        folder_resource_path = "/space/{}/folder".format(space_id)
        self._clickup_model = folder_resource_path
        result_2 = self._call(folder_resource_path, arguments=filters)

        data = []
        if result_1:
            for rec in result_1["lists"]:
                data.append(rec)
        if result_2:
            for rec in result_2["folders"]:
                for item in rec["lists"]:
                    data.append(item)
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
        return super(ProjectAdapter, self).create(data)

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
            return super(ProjectAdapter, self).write(external_id, data)
