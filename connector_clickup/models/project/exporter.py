import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from bs4 import BeautifulSoup
from odoo.osv import expression

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
                [("folder_id", "=", self.backend_record.uri)],
            ]
        )

        records = self.env["project.project"].search(domain)
        for record in records:
            self._export_record(record)

    def _export_record(self, record, job_options=None, **kwargs):
        """Delay the export of the records"""
        job_options = job_options or {}
        if "priority" not in job_options:
            job_options["priority"] = 5
        return super(ProjectProjectDelayedBatchExporter, self)._export_record(
            record, job_options, **kwargs
        )


class ProjectProjectImportMapper(Component):
    _name = "clickup.project.project.export.mapper"
    _inherit = "clickup.export.mapper"
    _apply_on = "clickup.project.project"
    _mapper_ext_key = "identifier"

    @mapping
    def name(self, record):
        name = record.name

        return {"name": name}

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
        content = record.folder_id

        return {"folder_id": content}

    @mapping
    def folder(self, record):
        content = record.folder

        return {"folder": content}
