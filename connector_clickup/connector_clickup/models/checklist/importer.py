import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.addons.connector.exception import MappingError

_logger = logging.getLogger(__name__)


class TaskChecklistImportMapper(Component):
    _name = "clickup.task.checklist.import.mapper"
    _inherit = "clickup.import.mapper"
    _apply_on = "clickup.task.checklist"
    _map_child_fallback = "clickup.map.child.import"

    children = [
        (
            "items",
            "clickup_checklist_item_ids",
            "clickup.checklist.item",
        ),
    ]
    direct = [("id", "external_id")]

    @only_create
    @mapping
    def odoo_id(self, record):
        """Creating odoo id"""
        task_checklist = self.get_binding(record, model=self._apply_on, value="id")
        if not task_checklist:
            return {}
        return {"odoo_id": task_checklist.id}

    @mapping
    def name(self, record):
        """Map name"""
        name = record.get("name")
        if not name:
            raise MappingError(_("Checklist must consist name"))
        return {"name": name}

    @mapping
    def backend_id(self, record):
        """Map backend Id"""
        return {"backend_id": self.backend_record.id}
