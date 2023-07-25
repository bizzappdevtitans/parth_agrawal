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
            force=True,
        )
        self.get_project_chats()
        for task in self.tasks:
            self.env["clickup.project.task"].import_record(
                backend=self.sudo().clickup_backend_id,
                external_id=task.clickup_bind_ids.external_id,
                force=True,
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

    def get_project_chats(self):
        """Get comments and attachments from clickup to project"""
        self.ensure_one()
        with self.clickup_backend_id.work_on("clickup.project.project") as work:
            backend_adapter = work.component(usage="backend.adapter")
            chat_dict = backend_adapter.get_chat(
                resource_path="/list/" + self.clickup_bind_ids.external_id + "/comment"
            )

            comments = chat_dict.get("comments", [])
            task_messages = (
                self.env["mail.message"]
                .sudo()
                .search([("res_id", "=", self.id), ("model", "=", "project.project")])
            )
            existing_external_ids = task_messages.mapped("external_id")

            for comment_data in comments:
                comment_id = comment_data.get("id", "")
                comment_text = comment_data.get("comment_text", "")

                commenter_email = comment_data.get("user", {}).get("email", "")

                if comment_id in existing_external_ids:
                    self.update_existing_message(
                        task_messages, comment_id, comment_text
                    )
                    continue

                # Attachments
                attachments = comment_data.get("comment", [])
                attachment_urls = self.get_attachment_urls(attachments)

                author_id = self.find_author(commenter_email)

                self.create_comment_with_attachments(
                    task_messages,
                    comment_id,
                    self.id,
                    comment_text,
                    author_id,
                    attachment_urls,
                )

    def update_existing_message(self, messages, external_id, comment_text):
        """Update comments and attachments from clickup to project"""
        existing_message = messages.filtered(lambda msg: msg.external_id == external_id)
        existing_message.write({"body": comment_text})

    def get_attachment_urls(self, attachments):
        """Get attachments url from clickup to project"""
        attachment_urls = []
        for attachment in attachments:
            if attachment.get("type") == "attachment":
                attachment_url = attachment.get("attachment", {}).get("url")
                if attachment_url:
                    attachment_urls.append(attachment_url)
        return attachment_urls

    def find_author(self, commenter_email):
        """Find the user to define author"""
        return (
            self.env["res.partner"]
            .sudo()
            .search([("email", "=", commenter_email)], limit=1)
        ).id or self.env.user.id

    def create_comment_with_attachments(
        self, messages, comment_id, res_id, comment_text, author_id, attachment_urls
    ):
        """Create comments and attachments from clickup to project"""
        new_message = messages.sudo().create(
            {
                "model": "project.project",
                "external_id": comment_id,
                "res_id": res_id,
                "message_type": "comment",
                "author_id": author_id,
                "body": comment_text,
            }
        )
        for attachment_url in attachment_urls:
            attachment_data = {
                "name": attachment_url.split("/")[-1],
                "url": attachment_url,
            }
            new_message.attachment_ids = [(0, 0, attachment_data)]


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
        folder = data.get("folder")
        if folder:
            resource_path = "/folder/{}/list".format(folder)
            self._clickup_model = resource_path
        else:
            if self.backend_record.test_mode:
                space_ids = (
                    self.backend_record.test_location.split(",")
                    if self.backend_record.test_location
                    else []
                )
            else:
                space_ids = (
                    self.backend_record.uri.split(",")
                    if self.backend_record.uri
                    else []
                )

            if space_ids:
                space_id = space_ids[0]  # Select the first space_id
                resource_path = "/space/{}/list".format(space_id)
                self._clickup_model = resource_path

        return super().create(data)

    def write(self, external_id, data):
        """Update records on the external system"""

        if external_id:
            resource_path = "/list/{}".format(external_id)
            self._clickup_model = resource_path
            return super().write(external_id, data)
