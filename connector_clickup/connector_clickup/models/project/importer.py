import logging
from datetime import date, timedelta

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.addons.connector.exception import MappingError

_logger = logging.getLogger(__name__)


class ProjectProjectImporter(Component):
    _name = "clickup.project.project.importer"
    _inherit = "clickup.importer"
    _apply_on = "clickup.project.project"


class ProjectProjectBatchImporter(Component):
    """Delay import of the records"""

    _name = "clickup.project.project.batch.importer"
    _inherit = "clickup.delayed.batch.importer"
    _apply_on = "clickup.project.project"

    def run(self, filters=None, force=False, job_options=None):
        """Run the synchronization"""
        records = self.backend_adapter.search(filters)
        for rec in records:
            for data in rec.get("lists", []):
                external_id = data.get(self.backend_adapter._clickup_ext_id_key)
                self._import_record(
                    external_id, data=data, force=force, job_options=job_options
                )


class ProjectProjectImportMapper(Component):
    _name = "clickup.project.project.import.mapper"
    _inherit = "clickup.import.mapper"
    _apply_on = "clickup.project.project"
    _mapper_ext_key = "identifier"

    @only_create
    @mapping
    def odoo_id(self, record):
        """Creating odoo id"""
        project = self.get_binding(record, model=self._apply_on, value="id")
        if not project:
            return {}
        return {"odoo_id": project.id}

    @mapping
    def name(self, record):
        """Map name"""
        name = record.get("name")
        if not name:
            raise MappingError(_("Project must consist name"))
        return {"name": name}

    @mapping
    def description(self, record):
        """Map description"""
        description = record.get("content")
        return {"description": description} if description else {}

    @mapping
    def backend_id(self, record):
        """Map the backend id"""
        backend = self.backend_record.id
        return {"backend_id": backend} if backend else {}

    @mapping
    def folder_id(self, record):
        """Map the folder id"""
        folder = record.get("folder").get("id")
        return {"folder_id": folder} if folder else {}

    @mapping
    def date_start(self, record):
        """Map the date start"""
        data_start = record.get("start_date")
        if not data_start:
            return {}
        timestamp = int(data_start) / 1000
        data_start = date.fromtimestamp(timestamp) + timedelta(days=1)
        return {"date_start": data_start}

    @mapping
    def date_end(self, record):
        """Map the date end"""
        data_end = record.get("due_date")
        if not data_end:
            return {}
        timestamp = int(data_end) / 1000
        data_end = date.fromtimestamp(timestamp) + timedelta(days=1)
        return {"date": data_end}

    @mapping
    def company_id(self, record):
        """Map company id"""
        company = self.backend_record.company_id.id
        if not company:
            raise MappingError(_("Company must be selected in backend"))
        return {"company_id": company}

    @mapping
    def team_id(self, record):
        """Map team id"""
        team_id = self.backend_record.team_id.external_id
        return {"team_id": team_id} if team_id else {}

    @mapping
    def color(self, record):
        """Map color field"""
        color_hex = record.get("status")
        if color_hex:
            color = color_hex.get("color")
            if color:
                color_integer = int(color.lstrip("#"), 16)
                return {"color": color_integer}
