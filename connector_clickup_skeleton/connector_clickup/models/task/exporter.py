import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class ProjectTaskExporter(Component):
    _name = "clickup.project.task.exporter"
    _inherit = "clickup.exporter"
    _apply_on = "clickup.project.tasks"


class ProjectTaskDelayedBatchExporter(Component):
    """Delay import of the records"""

    _name = "clickup.project.task.batch.exporter"
    _inherit = "clickup.delayed.batch.exporter"
    _apply_on = "clickup.project.tasks"

    def run(self, filters=None):
        """Run the synchronization"""
        filters = filters or {}
        domain = filters.get("domain", [])
        domain += [
            "|",
            ("clickup_bind_ids", "=", False),
            ("folder_id", "=", self.backend_record.uri),
        ]

        records = self.env["project.task"].search(domain)
        for record in records:
            self._export_record(record)

    def _export_record(self, record, job_options=None, **kwargs):
        """Delay the export of the records"""
        job_options = job_options or {}
        if "priority" not in job_options:
            job_options["priority"] = 5
        return super(ProjectTaskDelayedBatchExporter, self)._export_record(
            record, job_options, **kwargs
        )


class ProjectTaskImportMapper(Component):
    _name = "clickup.project.task.export.mapper"
    _inherit = "clickup.export.mapper"
    _apply_on = "clickup.project.tasks"
    _mapper_ext_key = "identifier"

    @mapping
    def name(self, record):
        name = record.name

        return {"name": name}

    @mapping
    def description(self, record):
        content = record.description

        return {"description": content}

    @mapping
    def project_id(self, record):
        content = record.project_id.external_id

        return {"project_id": content}
