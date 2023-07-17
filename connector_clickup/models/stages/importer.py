import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.addons.connector.exception import MappingError

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

    def run(self, filters=None, force=False, job_options=None):
        """Run the synchronization"""

        records = self.backend_adapter.search_read(filters)

        for rec in records:
            for status in rec.get("statuses", []):
                external_id = status.get(self.backend_adapter._clickup_ext_id_key)
                self._import_record(
                    external_id, data=status, force=force, job_options=job_options
                )


class ProjectTaskTypeImportMapper(Component):
    _name = "clickup.project.task.type.import.mapper"
    _inherit = "clickup.import.mapper"
    _apply_on = "clickup.project.task.type"

    def _check_stage(self, record):
        name = record.get("status")
        stage_name = self.env["project.task.type"].search([("name", "=", name)])
        return stage_name

    @only_create
    @mapping
    def odoo_id(self, record):
        """Creating odoo id"""
        stage_name = self._check_stage(record)
        if not stage_name:
            stage = self.get_binding(record, model=self._apply_on, value="id")
            if not stage:
                return {}
            return {"odoo_id": stage.id}
        return {}

    @mapping
    def name(self, record):
        """Map name"""
        stage_name = self._check_stage(record)
        if not stage_name:
            return {"name": record.get("status")}
        if stage_name:
            raise MappingError(_("'%s' Stage already exist") % stage_name.name)

    @mapping
    def backend_id(self, record):
        """Map the backend id"""
        stage_name = self._check_stage(record)
        if not stage_name:
            return {"backend_id": self.backend_record.id}
        return {}
