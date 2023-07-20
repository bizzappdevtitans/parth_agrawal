import datetime
import logging

from bs4 import BeautifulSoup

from odoo.osv import expression

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class ProjectProjectExporter(Component):
    _name = "clickup.project.project.exporter"
    _inherit = "clickup.exporter"
    _apply_on = "clickup.project.project"


class ProjectProjectDelayedBatchExporter(Component):
    """Delay import of the records"""

    _name = "clickup.project.project.batch.exporter"
    _inherit = "clickup.delayed.batch.exporter"
    _apply_on = "clickup.project.project"

    def run(self, filters=None, job_options=None):
        """Run the synchronization"""
        filters = filters or {}
        domain = expression.OR(
            [
                [("clickup_bind_ids", "=", False)],
                [("clickup_backend_id", "=", self.backend_record.id)],
            ]
        )

        records = self.env["project.project"].search(domain)
        for record in records:
            self._export_record(record, job_options=job_options)


class ProjectProjectImportMapper(Component):
    _name = "clickup.project.project.export.mapper"
    _inherit = "clickup.export.mapper"
    _apply_on = "clickup.project.project"
    _mapper_ext_key = "identifier"

    def date_to_timestamp(self, date=False):
        date_object = datetime.datetime.strptime(str(date), "%Y-%m-%d")
        midnight = datetime.datetime.combine(date_object, datetime.time.min)
        epoch_timestamp = int(midnight.timestamp() * 1000)
        return epoch_timestamp

    @mapping
    def name(self, record):
        """Mapped name"""
        return {"name": record.name}

    @mapping
    def content(self, record):
        """Mapped description"""
        content = record.description
        if not content:
            return {}
        soup = BeautifulSoup(content, "html.parser")
        content = soup.get_text()

        return {"content": content}

    @mapping
    def due_date(self, record):
        date = record.date
        if date:
            epoch_timestamp = self.date_to_timestamp(date=date)

            return {"due_date": epoch_timestamp}

    @mapping
    def start_date(self, record):
        date = record.date_start
        if date:
            epoch_timestamp = self.date_to_timestamp(date=date)
            return {"start_date": epoch_timestamp}

    @mapping
    def folder_id(self, record):
        """Mapped folder id"""
        return {"folder_id": record.folder_id}

    @mapping
    def folder(self, record):
        """Mapped folder info"""
        return {"folder": record.folder_info}
