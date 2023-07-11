import logging
from datetime import datetime

from bs4 import BeautifulSoup

from odoo.osv import expression

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class ProjectTaskExporter(Component):
    _name = "clickup.project.task.exporter"
    _inherit = "clickup.exporter"
    _apply_on = "clickup.project.task"


class ProjectTaskDelayedBatchExporter(Component):
    """Delay import of the records"""

    _name = "clickup.project.task.batch.exporter"
    _inherit = "clickup.delayed.batch.exporter"
    _apply_on = "clickup.project.task"

    def run(self, filters=None):
        """Run the synchronization"""
        filters = filters or {}
        domain = expression.OR(
            [
                [("clickup_bind_ids", "=", False)],
                [("clickup_backend_id", "=", self.backend_record.id)],
            ]
        )

        records = self.env["project.task"].search(domain)
        for record in records:
            self._export_record(record, model=self._apply_on)


class ProjectTaskImportMapper(Component):
    _name = "clickup.project.task.export.mapper"
    _inherit = "clickup.export.mapper"
    _apply_on = "clickup.project.task"
    _mapper_ext_key = "identifier"

    @mapping
    def name(self, record):
        """Mapped name"""
        name = record.name

        return {"name": name}

    @mapping
    def description(self, record):
        """Mapped description"""
        content = record.description
        if content:
            soup = BeautifulSoup(content, "html.parser")
            content = soup.get_text()

            return {"description": content}

    @mapping
    def project_id(self, record):
        """Mapped project_id"""

        return {"project_id": record.project_id.external_id}

    @mapping
    def due_date(self, record):
        """Mapped due date"""
        data = record.date_deadline

        if data:
            date_object = datetime.strptime(str(data), "%Y-%m-%d")

            unix_timestamp = int(date_object.timestamp() * 1000)

            return {"due_date": str(unix_timestamp)}

    @mapping
    def status(self, record):
        """Mapped stage"""

        return {"status": record.stage_id.name}
