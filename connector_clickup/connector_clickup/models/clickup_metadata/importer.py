import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class ClickupTeamImportMapper(Component):
    _name = "clickup.team.import.mapper"
    _inherit = "clickup.import.mapper"
    _apply_on = "clickup.team"

    @mapping
    def team(self, record):
        """#T-02421 Mapping for code"""
        code = record.get("id")
        return {"team": code}

    @mapping
    def backend_id(self, record):
        """#T-02421 Mapping for backend"""
        return {"backend_id": self.backend_record.id}

    @mapping
    def name(self, record):
        """#T-02421 Mapping for label"""
        label = record.get("name")
        return {"name": label}


class ClickupTeamBatchImporter(Component):
    """
    Import Clickup Team details
    """

    _name = "clickup.team.batch.importer"
    _inherit = "clickup.delayed.batch.importer"
    _apply_on = "clickup.team"

    def run(self, filters=None, force=False, job_options=None):
        """Run the synchronization"""
        records = self.backend_adapter.search(filters)
        for rec in records.get("teams", []):
            external_id = rec.get(self.backend_adapter._clickup_ext_id_key)
            self._import_record(
                external_id, data=rec, force=force, job_options=job_options
            )


class ClickupTeamImporter(Component):
    _name = "clickup.team.importer"
    _inherit = "clickup.importer"
    _apply_on = "clickup.team"
