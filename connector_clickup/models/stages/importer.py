import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.addons.connector.exception import MappingError

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
        stage = self._get_binding_values(record, model=self._apply_on, value="id")

        name = record.get("status")
        stage_name = self.env["project.task.type"].search([("name", "=", name)])
        if stage_name:
            return {"odoo_id": stage_name.id}

        else:
            return {"odoo_id": stage.id}
        return {}

    @mapping
    def name(self, record):
        name = record.get("status")

        stage_name = self.env["project.task.type"].search([("name", "=", name)])
        if not stage_name:
            return {"name": name}
        if stage_name:
            raise MappingError(_("'%s' Stage already exist") % stage_name.name)

    def external_id(self, record):
        """#T-02383 Mapped external id"""
        external_id = record.get("id")

        return {"external_id": external_id}

    @mapping
    def backend_id(self, record):
        """Mapped the backend id"""

        backend_id = self.backend_record.id

        return {"backend_id": backend_id}
