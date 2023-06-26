import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

# from ..exception import MappingError

# from odoo.addons import queue_job

_logger = logging.getLogger(__name__)


class ProjectTaskTypeImporter(Component):
    _name = "clickup.project.task.type.importer"
    _inherit = "clickup.importer"
    _apply_on = "clickup.project.task.type"


class ProjectTaskTypeBatchImporter(Component):
    """Delay import of the records"""

    _name = "clickup.project.task.type.batch.importer"
    _inherit = "clickup.delayed.batch.importer"
    _apply_on = "clickup.project.task.type"

    # 1 def run(self, filters=None, force=False):
    #     """Run the synchronization"""

    #     records = self.backend_adapter.search(filters)

    #     for record in records["folders"]:
    #         for item in record["lists"]:
    #             for data in item["statuses"]:
    #                 external_id = data.get(self.backend_adapter._clickup_ext_id_key)

    #                 self._import_record(
    #                     external_id, data=data, force=force, model=self._apply_on
    #                 )

    # 2 def run(self, filters=None, force=False):
    #     """Run the synchronization"""

    #     records = self.backend_adapter.search_read(filters)
    #     print("\n\nFull records=\n\n", records)

    #     for item in records.get("folders"):
    #         print("\n\nFolder=\n\n", item)
    #         for data in item.get("lists", []):
    #             print("\n\nlist=\n\n", data)
    #             for status in data.get("statuses", []):
    #                 print("\n\nstatus=\n\n", status)
    #                 external_id = status.get(self.backend_adapter._clickup_ext_id_key)

    #                 self._import_record(
    #                     external_id, data=status, force=force, model=self._apply_on
    #                 )

    def run(self, filters=None, force=False):
        """Run the synchronization"""

        records = self.backend_adapter.search_read(filters)

        for rec in records:
            for status in rec.get("statuses", []):
                external_id = status.get(self.backend_adapter._clickup_ext_id_key)
                self._import_record(
                    external_id, data=status, force=force, model=self._apply_on
                )


class ProjectTaskTypeImportMapper(Component):
    _name = "clickup.project.task.type.import.mapper"
    _inherit = "clickup.import.mapper"
    _apply_on = "clickup.project.task.type"

    @only_create
    @mapping
    def odoo_id(self, record):
        """Getting product based on the SKU."""

        binder = self.binder_for(model="clickup.project.task.type")
        stage = binder.to_internal(record.get("id"), unwrap=True)

        if not stage:
            return {}
        return {"odoo_id": stage.id}

    @mapping
    def name(self, record):
        name = record.get("status")

        stage_name = self.env["project.task.type"].search([("name", "=", name)])
        if not stage_name:
            return {"name": name}
        else:
            queue_job = self.env["queue.job"].search(
                [("job_function_id", "=", "<clickup.project.task.type>.import_record")]
            )
            queue_job.write(
                {
                    "state": "done",
                    "result": "Stage already exist in project.task.type model",
                }
            )

            # return _("%s stage is already exist in project.task.type model.") % name

    def external_id(self, record):
        """#T-02383 Mapped external id"""
        external_id = record.get("id")

        return {"external_id": external_id}

    @mapping
    def backend_id(self, record):
        """Mapped the backend id"""

        backend_id = self.backend_record.id

        return {"backend_id": backend_id}
