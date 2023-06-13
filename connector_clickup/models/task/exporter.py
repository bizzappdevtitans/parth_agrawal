import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from datetime import datetime, time
from bs4 import BeautifulSoup
from odoo.osv import expression


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
        domain = expression.OR(
            [
                [("clickup_bind_ids", "=", False)],
                [("folder_id", "=", self.backend_record.uri)],
            ]
        )

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
        if not content:
            return {}
        soup = BeautifulSoup(content, "html.parser")
        content = soup.get_text()

        return {"description": content}

    @mapping
    def project_id(self, record):
        content = record.project_id.external_id

        return {"project_id": content}

    @mapping
    def due_date(self, record):
        data = record.date_deadline

        if data:
            date_object = datetime.strptime(str(data), "%Y-%m-%d")

            unix_timestamp = int(date_object.timestamp() * 1000)

            return {"due_date": str(unix_timestamp)}

    @mapping
    def status(self, record):
        data = record.stage_id.name

        if data:
            return {"status": data}
