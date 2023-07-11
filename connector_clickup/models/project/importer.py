import logging
from datetime import date, timedelta

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

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

    def run(self, filters=None, force=False):
        """Run the synchronization"""

        records = self.backend_adapter.search(filters)

        for rec in records:
            for data in rec.get("lists", []):
                external_id = data.get(self.backend_adapter._clickup_ext_id_key)
                self._import_record(
                    external_id, data=data, force=force, model=self._apply_on
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
        return {"name": record.get("name")}

    @mapping
    def description(self, record):
        """Map description"""
        return {"description": record.get("content")}

    @mapping
    def external_id(self, record):
        """#Map external id"""
        return {"external_id": record.get("id")}

    @mapping
    def backend_id(self, record):
        """Map the backend id"""

        return {"backend_id": self.backend_record.id}

    @mapping
    def folder_id(self, record):
        """Map the folder id"""

        return {"folder_id": record.get("folder").get("id")}

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

        return {"company_id": self.backend_record.company_id.id}

    @mapping
    def team_id(self, record):
        """Map team id"""
        return {"team_id": self.backend_record.team_id}
