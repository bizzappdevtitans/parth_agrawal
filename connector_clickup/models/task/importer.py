import base64
import logging
from datetime import date, datetime, timedelta

import requests

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.addons.connector.exception import MappingError

_logger = logging.getLogger(__name__)


class ProjectTaskImporter(Component):
    _name = "clickup.project.task.importer"
    _inherit = "clickup.importer"
    _apply_on = "clickup.project.task"

    def _is_uptodate(self, binding):
        """
        Return True if the import should be skipped because
        it is already up-to-date in OpenERP
        """
        # if the last synchronization date is greater than the last
        # update in clickup, we skip the import.
        # Important: at the beginning of the exporters flows, we have to
        # check if the clickup_date is more recent than the sync_date
        # and if so, schedule a new import. If we don't do that, we'll
        # miss changes done in clickup
        super()._is_uptodate(binding)
        assert self.clickup_record
        last_update_date = self.backend_adapter._last_update_date
        update_date = self.clickup_record.get(last_update_date, "")
        timestamp = int(update_date) / 1000
        if (
            not update_date
            or not binding
            or (binding and not hasattr(binding, "updated_at"))
        ):
            return  # no update date on clickup, always import it.
        sync_date = binding.updated_at
        if not sync_date:
            return
        clickup_date = datetime.fromtimestamp(timestamp)
        return clickup_date <= sync_date

    def _import_dependencies(self):
        """
        Import the dependencies for the record
        Import of dependencies can be done manually or by calling
        :meth:`_import_dependency` for each dependency.
        """
        if not hasattr(self.backend_adapter, "_model_dependencies"):
            return

        for dependency in self.backend_adapter._model_dependencies:
            model, key = dependency
            external_id = self.clickup_record.get(key).get("id")

            self._import_dependency(external_id=external_id, binding_model=model)


class ProjectTaskBatchImporter(Component):
    """Delay import of the records"""

    _name = "clickup.project.task.batch.importer"
    _inherit = "clickup.delayed.batch.importer"
    _apply_on = "clickup.project.task"

    def run(self, filters=None, force=False, job_options=None):
        """Run the synchronization"""
        from_date = filters.pop("from_date", None)
        to_date = filters.pop("to_date", None)
        records = self.backend_adapter.search(
            filters, from_date=from_date, to_date=to_date
        )

        for record in records:
            tasks = record.get("tasks", [])
            for task in tasks:
                external_id = task.get(self.backend_adapter._clickup_ext_id_key)

                self._import_record(
                    external_id, data=task, force=force, job_options=job_options
                )


class ProjectTaskImportMapper(Component):
    _name = "clickup.project.task.import.mapper"
    _inherit = "clickup.import.mapper"
    _apply_on = "clickup.project.task"
    _map_child_fallback = "clickup.map.child.import"

    # children = [
    #     (
    #         "assignees",
    #         "user_ids",
    #         "clickup.res.users",
    #     )
    # ]

    @only_create
    @mapping
    def odoo_id(self, record):
        """Creating odoo id"""
        task = self.get_binding(record, model=self._apply_on, value="id")
        if not task:
            return {}
        return {"odoo_id": task.id}

    @mapping
    def project_id(self, record):
        """Map project id"""
        project_id = record.get("list").get("id")
        binder = self.binder_for("clickup.project.project")
        project = binder.to_internal(project_id, unwrap=True)
        if project:
            return {"project_id": project.id}

    @mapping
    def stage_id(self, record):
        """Map stage id"""
        stage_id = record.get("status").get("status")
        stage = self.env["project.task.type"].search([("name", "=", stage_id)], limit=1)
        if not stage:
            raise MappingError(_("Stage not exist"))
        return {"stage_id": stage.id}

    @mapping
    def name(self, record):
        """Map name"""
        name = record.get("name")
        return {
            "name": name,
        }

    @mapping
    def description(self, record):
        """Map description"""

        return {"description": record.get("text_content")}

    @mapping
    def backend_id(self, record):
        """Map backend id"""

        return {"backend_id": self.backend_record.id}

    @mapping
    def project_info(self, record):
        """Map project info"""

        return {"project_info": record.get("list").get("id")}

    @mapping
    def date_deadline(self, record):
        """Map date deadline"""
        due_data = record.get("due_date")

        if due_data:
            timestamp = int(due_data) / 1000
            due_date = date.fromtimestamp(timestamp) + timedelta(days=1)
            return {"date_deadline": due_date}

    @mapping
    def created_at(self, record):
        """Map created at"""
        created_at = record.get("date_created")
        if created_at:
            timestamp = int(created_at) / 1000
            date_created = datetime.fromtimestamp(timestamp)
            return {"created_at": date_created}
        else:
            return {}

    @mapping
    def updated_at(self, record):
        """Map updated at"""
        updated_at = record.get("date_updated")
        if updated_at:
            timestamp = int(updated_at) / 1000
            date_updated = datetime.fromtimestamp(timestamp)
            return {"updated_at": date_updated}
        else:
            return {}

    @mapping
    def company_id(self, record):
        """Map company id"""

        return {"company_id": self.backend_record.company_id.id}

    @mapping
    def assignee_id(self, record):
        """Map assignee id"""
        assignees = record.get("assignees", [])
        if not assignees:
            return {"user_ids": self.env.user}
        assignee_ids = []
        for assignee in assignees:
            user_name = assignee.get("username")
            email = assignee.get("email")
            login = assignee.get("id")
            user = self.env["res.users"].search(
                [
                    ("login", "=", login),
                    ("email", "=", email),
                ],
                limit=1,
            )
            picture_url = assignee.get("profilePicture")
            response = requests.get(picture_url, timeout=10)
            if response.status_code == 200:
                picture_data = response.content
                picture_base64 = base64.b64encode(picture_data)

            if user:
                assignee_ids.append(user.id)
            if not user:
                new_user = self.env["res.users"].create(
                    {
                        "name": user_name,
                        "login": login,
                        "email": email,
                        "image_1920": picture_base64,
                    }
                )
                assignee_ids.append(new_user.id)
        return {"user_ids": assignee_ids}

    # @mapping
    # def assignee_id(self, record):
    #     """Map assignee id and profile picture"""
    #     assignees = record.get("assignees", [])
    #     if not assignees:
    #         return {"user_ids": self.env.user}
    #     assignee_ids = []
    #     for assignee in assignees:
    #         user_name = assignee.get("username")
    #         email = assignee.get("email")
    #         picture_url = assignee.get("profilePicture")
    #         login = assignee.get("id")
    #         user = self.env["res.users"].search(
    #             [
    #                 ("login", "=", login),
    #                 ("email", "=", email),
    #             ],
    #             limit=1,
    #         )
    #         if not user:
    #             response = requests.get(picture_url)
    #             if response.status_code == 200:
    #                 picture_data = response.content
    #                 picture_base64 = base64.b64encode(picture_data)
    #                 new_user = self.env["res.users"].create(
    #                     {
    #                         "name": user_name,
    #                         "login": login,
    #                         "email": email,
    #                         "image_1920": picture_base64,
    #                     }
    #                 )
    #                 assignee_ids.append(new_user.id)
    #         else:
    #             assignee_ids.append(user.id)
    #     return {"user_ids": assignee_ids}

    def finalize(self, map_record, values):
        """Tags mapping through child mapper"""
        record = map_record.source

        tags = record.get("tags")
        tag_ids = []

        if tags:
            for tag_name in tags:
                tag_name = tag_name.get("name")
                if tag_name:
                    existing_label = self.env["project.tags"].search(
                        [("name", "=", tag_name)]
                    )
                    if existing_label:
                        tag_ids.append(existing_label.id)
                    else:
                        new_label = self.env["project.tags"].create({"name": tag_name})
                        tag_ids.append(new_label.id)
        values["tag_ids"] = [(6, 0, tag_ids)]
        return values
