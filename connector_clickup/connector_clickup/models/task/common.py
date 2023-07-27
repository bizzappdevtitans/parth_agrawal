from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.component.core import Component

from ...components.misc import (
    create_comment_with_attachments,
    find_author,
    get_attachment_urls,
    update_existing_message,
)


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


class MailMessage(models.Model):
    _inherit = "mail.message"

    external_id = fields.Char()


class ProjectTask(models.Model):
    _inherit = "project.task"

    clickup_bind_ids = fields.One2many(
        "clickup.project.task",
        "odoo_id",
        string="Clickup Backend ID",
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
    estimated_cost = fields.Char()

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
            force=True,
        )
        self.get_task_chats()

    def update_export_task(self):
        """Update task from odoo to Clickup website"""
        self.ensure_one()
        if not self.clickup_backend_id:
            raise UserError(_("Please add backend!!!"))
        self.env["clickup.project.task"].export_record(
            backend=self.sudo().clickup_backend_id, record=self
        )
        self.update_checklist()

    def export_task_to_clickup(self):
        """Export newly created task from odoo to clickup website"""
        self.ensure_one()
        if not self.project_id.clickup_backend_id:
            raise UserError(_("Please select project that consist backend!!!"))
        try:
            self.env["clickup.project.task"].export_record(
                backend=self.sudo().project_id.clickup_backend_id, record=self
            )
        except Exception as err:
            raise UserError from err()
        self.ensure_one()
        if not self.clickup_backend_id:
            raise UserError(_("Please add backend!!!"))
        self.env["clickup.project.task"].export_record(
            backend=self.sudo().clickup_backend_id, record=self
        )

    def get_task_chats(self):
        """Get comments and attachments from clickup to task"""
        self.ensure_one()
        with self.clickup_backend_id.work_on("clickup.project.task") as work:
            backend_adapter = work.component(usage="backend.adapter")
            chat_dict = backend_adapter.get_chat(
                resource_path="/task/" + self.clickup_bind_ids.external_id + "/comment"
            )
            comments = chat_dict.get("comments", [])
            messages = (
                self.env["mail.message"]
                .sudo()
                .search([("res_id", "=", self.id), ("model", "=", "project.task")])
            )
            existing_external_ids = messages.mapped("external_id")
            for comment_data in comments:
                comment_id = comment_data.get("id", "")
                comment_text = comment_data.get("comment_text", "")
                commenter_email = comment_data.get("user", {}).get("email", "")
                if comment_id in existing_external_ids:
                    update_existing_message(self, messages, comment_id, comment_text)
                    continue
                # Attachments
                attachments = comment_data.get("comment", [])
                attachment_urls = get_attachment_urls(self, attachments)
                author_id = find_author(self, commenter_email)
                create_comment_with_attachments(
                    self,
                    messages,
                    comment_id,
                    self.id,
                    comment_text,
                    author_id,
                    attachment_urls,
                    model=self._name,
                )

    def update_checklist(self):
        """Update checklist items in ClickUp based on the state"""
        self.ensure_one()
        with self.clickup_backend_id.work_on("clickup.project.task") as work:
            backend_adapter = work.component(usage="backend.adapter")
            for record in self.checklists:
                resolved_status = record.state == "done"
                backend_adapter.set_checklist(
                    resource_path="/checklist/"
                    + record.parent_checklist
                    + "/checklist_item/"
                    + record.item_id,
                    arguments={"resolved": resolved_status},
                )


class TaskAdapter(Component):
    _name = "clickup.project.task.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.project.task"
    _clickup_model = "/task"
    _clickup_ext_id_key = "id"
    _model_dependencies = [
        (
            "clickup.project.project",
            "list",
        ),
    ]

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
        clickup_model = self._clickup_model
        for space_id in space_ids:
            clickup_model = "/space/{}/folder".format(space_id)
            folder_project_payload = self._call(clickup_model, arguments=filters)
            if folder_project_payload:
                for record in folder_project_payload.get("folders", []):
                    items = record.get("id")
                    folder_ids.append(items)
            for folder_id in folder_ids:
                clickup_model = "/folder/{}/list".format(folder_id)
                folder_payload = self._call(clickup_model, arguments=filters)
                data.append(folder_payload)
            clickup_model = "/space/{}/list".format(space_id)
            space_project_payload = self._call(clickup_model, arguments=filters)
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
            clickup_model = "/list/{}/task".format(external_id)
            task_payload = self._call(clickup_model, arguments=filters)
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
