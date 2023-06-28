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

    def run(self, filters=None):
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
            self._export_record(record, model=self._apply_on)


class ProjectProjectImportMapper(Component):
    _name = "clickup.project.project.export.mapper"
    _inherit = "clickup.export.mapper"
    _apply_on = "clickup.project.project"
    _mapper_ext_key = "identifier"

    @mapping
    def name(self, record):
        return {"name": record.name}

    @mapping
    def content(self, record):
        content = record.description
        if not content:
            return {}
        soup = BeautifulSoup(content, "html.parser")
        content = soup.get_text()

        return {"content": content}

    @mapping
    def folder_id(self, record):
        return {"folder_id": record.folder_id}

    @mapping
    def folder(self, record):
        return {"folder": record.folder_info}
