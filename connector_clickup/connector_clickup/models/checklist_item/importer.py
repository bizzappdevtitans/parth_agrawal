import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.addons.connector.exception import MappingError

_logger = logging.getLogger(__name__)


class ChecklistItemImportMapper(Component):
    _name = "clickup.checklist.item.import.mapper"
    _inherit = "clickup.import.mapper"
    _apply_on = "clickup.checklist.item"

    direct = [("id", "external_id")]

    @only_create
    @mapping
    def odoo_id(self, record):
        """Creating odoo id"""
        checklist_item = self.get_binding(record, model=self._apply_on, value="id")
        if not checklist_item:
            return {}
        return {"odoo_id": checklist_item.id}

    @mapping
    def name(self, record):
        """Map name"""
        name = record.get("name")
        if not name:
            raise MappingError(_("Checklist must consist name"))
        return {"name": name}

    @mapping
    def state(self, record):
        """Map the state"""
        state = record.get("resolved")
        if state is True:
            return {"state": "done"}
        return {"state": "todo"}

    @mapping
    def backend_id(self, record):
        """Map backend Id"""
        return {"backend_id": self.backend_record.id}
