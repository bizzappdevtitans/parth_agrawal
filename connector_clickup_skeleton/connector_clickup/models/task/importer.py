import logging
from datetime import date

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

_logger = logging.getLogger(__name__)


class ProjectTaskImporter(Component):
    _name = "clickup.project.task.importer"
    _inherit = "clickup.importer"
    _apply_on = "clickup.project.tasks"

    def __init__(self, work_context):
        """Inherit init method."""
        work_context.model = work_context.model.with_context(
            create_product_product=False
        )
        super(ProjectTaskImporter, self).__init__(work_context)

    def _after_import(self, binding, **kwargs):
        """Hook called at the end of the import"""

        return super(ProjectTaskImporter, self)._after_import(binding, **kwargs)


class ProjectTaskBatchImporter(Component):
    """Delay import of the records"""

    _name = "clickup.project.task.batch.importer"
    _inherit = "clickup.delayed.batch.importer"
    _apply_on = "clickup.project.tasks"

    def run(self, filters=None, force=False):
        """Run the synchronization"""

        records = self.backend_adapter.search(filters)

        for record in records:
            tasks = record.get("tasks", [])
            for task in tasks:
                external_id = task.get(self.backend_adapter._clickup_ext_id_key)

                self._import_record(external_id, data=task, force=force)


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
            return {"name": name, "project_id": project.id, "stage_id": stage}
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
    def api_token(self, record):
        """Mapped the backend id"""
        data = self.backend_record.api_key

        return {"api_token_data": data}

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
            due_date = date.fromtimestamp(timestamp)
            return {"date_deadline": due_date}
