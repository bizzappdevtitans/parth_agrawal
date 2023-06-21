import logging
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from datetime import datetime, date, timedelta

_logger = logging.getLogger(__name__)


class ProjectTaskImporter(Component):
    _name = "clickup.project.task.importer"
    _inherit = "clickup.importer"
    _apply_on = "clickup.project.tasks"

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
        super(ProjectTaskImporter, self)._is_uptodate(binding)
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

    def _before_import(self):
        """
        Hook called before the import, when we have the clickup
        data
        """
        # res = super(ProjectTaskImporter, self)._before_import()

        # tags_payload = self.clickup_record.get("tags")
        # print("\n\nTag Payload\n\n", tags_payload)
        # data = []
        # data.append(tags_payload[0].get("name"))
        # print("data ==", data)
        # Tag = self.env["project.tags"]
        # for record in data:
        #     if record in Tag:
        #         continue

        #     Tag.create({"name": record})
        # return res

        res = super(ProjectTaskImporter, self)._before_import()

        # tags_payload = self.clickup_record
        # print("\n\nTag Payload\n\n", tags_payload)
        # data = []
        # for record in tags_payload["tags"]:
        #     name = record.get("name")
        #     print("record printed =", record)
        #     data.append(name)
        # print("data ==", data)
        # Tag = self.env["project.tags"]
        # for record in data:
        #     print("record in data ==", record)
        #     if record not in Tag:
        #         Tag.create({"name": record})
        #     else:
        #         print("inside else condition")
        #         continue
        return res


class ProjectTaskBatchImporter(Component):
    """Delay import of the records"""

    _name = "clickup.project.task.batch.importer"
    _inherit = "clickup.delayed.batch.importer"
    _apply_on = "clickup.project.tasks"

    def run(self, filters=None, force=False):
        """Run the synchronization"""

        records = self.backend_adapter.search(filters)
        print("\n\nTask records\n\n", records)
        for record in records:
            tasks = record.get("tasks", [])
            for task in tasks:
                external_id = task.get(self.backend_adapter._clickup_ext_id_key)

                self._import_record(
                    external_id, data=task, force=force, model=self._apply_on
                )


class ProjectTaskImportMapper(Component):
    _name = "clickup.project.task.import.mapper"
    _inherit = "clickup.import.mapper"
    _apply_on = "clickup.project.tasks"

    @only_create
    @mapping
    def odoo_id(self, record):
        """Getting product based on the SKU."""

        binder = self.binder_for(model="clickup.project.tasks")
        odoo_id = binder.to_internal(record.get("id"), unwrap=True)

        if not odoo_id:
            return {}
        return {"odoo_id": odoo_id.id}

    @mapping
    def name(self, record):
        project_id = record.get("list").get("id")

        project = self.env["project.project"].search([("external_id", "=", project_id)])

        stage_id = record.get("status").get("status")
        stage = self.env["project.task.type"].search([("name", "=", stage_id)], limit=1)
        if project and stage:
            name = record.get("name")
            return {"name": name, "project_id": project.id, "stage_id": stage.id}
        else:
            _logger.warning(
                "Project or Stage not found for external ID: %s", project_id
            )

    @mapping
    def description(self, record):
        content = record.get("text_content")

        return {"description": content}

    @mapping
    def external_id(self, record):
        """#T-02383 Mapped external id"""

        external_id = record.get("id")

        return {"external_id": external_id}

    @mapping
    def backend_id(self, record):
        """Mapped the backend id"""
        data = self.backend_record.id

        return {"backend_id": data}

    @mapping
    def folder_id(self, record):
        """Mapped the backend id"""
        data = self.backend_record.uri

        return {"folder_id": data}

    @mapping
    def date_deadline(self, record):
        """Mapped the backend id"""
        data = record.get("due_date")

        if data:
            timestamp = int(data) / 1000
            due_date = date.fromtimestamp(timestamp) + timedelta(days=1)
            return {"date_deadline": due_date}

    @mapping
    def created_at(self, record):
        """Mapped the backend id"""
        created = record.get("date_created")
        if created:
            timestamp = int(created) / 1000
            date_updated = datetime.fromtimestamp(timestamp)
            return {"created_at": date_updated}
        else:
            return {}

    @mapping
    def updated_at(self, record):
        """Mapped the backend id"""

        updated = record.get("date_updated")
        if updated:
            timestamp = int(updated) / 1000
            date_updated = datetime.fromtimestamp(timestamp)
            return {"updated_at": date_updated}
        else:
            return {}

    # @mapping
    # def tag_ids(self, record):
    #     """Map the backend id"""
    #     commands = []
    #     Tag = self.env["project.tags"]
    #     for data in record["tags"]:
    #         tag_name = data.get("name")
    #         if tag_name:
    #             tag = Tag.search([("name", "=", tag_name)])
    #             print("tag of mapping", tag)
    #             if tag:
    #                 commands.append([(6, 0, tag.ids)])
    #     return {"tag_ids": commands}
