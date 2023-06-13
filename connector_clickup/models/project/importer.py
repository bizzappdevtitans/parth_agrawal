import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from datetime import datetime, date, timedelta


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

        for record in records["lists"]:
            external_id = record.get(self.backend_adapter._clickup_ext_id_key)

            self._import_record(external_id, data=record, force=force)


class ProjectProjectImportMapper(Component):
    _name = "clickup.project.project.import.mapper"
    _inherit = "clickup.import.mapper"
    _apply_on = "clickup.project.project"
    _mapper_ext_key = "identifier"

    @only_create
    @mapping
    def odoo_id(self, record):
        """Getting product based on the SKU."""

        binder = self.binder_for(model="clickup.project.project")
        odoo_id = binder.to_internal(record.get("id"), unwrap=True)

        if not odoo_id:
            return {}
        return {"odoo_id": odoo_id.id}

    @mapping
    def name(self, record):
        name = record.get("name")

        return {"name": name}

    @mapping
    def description(self, record):
        content = record.get("content")

        return {"description": content}

    @mapping
    def external_id(self, record):
        """#T-02383 Mapped external id"""
        external_id = record.get("id")

        return {"external_id": external_id}

    @mapping
    def backend_id(self, record):
        """Mapped the backend id"""
        data = self.backend_record.id

        return {"backend_id": data}

    @mapping
    def folder_id(self, record):
        """Mapped the backend id"""
        data = self.backend_record.uri

        return {"folder_id": data}

    @mapping
    def synced_at(self, record):
        """Mapped the backend id"""
        data = datetime.now()

        return {"synced_at": data}

    @mapping
    def date_start(self, record):
        """Mapped the backend id"""
        data_start = record.get("start_date")
        if not data_start:
            return {}

        timestamp = int(data_start) / 1000
        data_start = date.fromtimestamp(timestamp) + timedelta(days=1)
        return {"date_start": data_start}

    @mapping
    def date_end(self, record):
        """Mapped the backend id"""
        data_end = record.get("due_date")
        if not data_end:
            return {}
        timestamp = int(data_end) / 1000
        data_end = date.fromtimestamp(timestamp) + timedelta(days=1)
        return {"date": data_end}
