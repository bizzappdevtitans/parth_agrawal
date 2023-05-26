import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

_logger = logging.getLogger(__name__)


class ProjectTaskImporter(Component):
    _name = "clickup.project.task.importer"
    _inherit = "clickup.importer"
    _apply_on = "clickup.project.tasks"


class ProjectTaskBatchImporter(Component):
    """Delay import of the records"""

    _name = "clickup.project.task.batch.importer"
    _inherit = "clickup.delayed.batch.importer"
    _apply_on = "clickup.project.tasks"


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

        stage_id = record.get("status")
        stage = self.env["project.task.type"].search([("external_id", "=", stage_id)])

        if project and stage:
            name = record.get("name")
            return {"name": name, "project_id": project.id, "stage_id": stage.id}
        else:
            _logger.warning(
                "Project or Stage not found for external ID: %s", project_id, stage
            )
        return {}

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
