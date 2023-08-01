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

    # @only_create
    # @mapping
    # def odoo_id(self, record):
    #     """Creating odoo id"""
    #     checklist_item_id = record.get("id")
    #     binder = self.binder_for("clickup.checklist.item")
    #     checklist_item = binder.to_internal(checklist_item_id, unwrap=True)
    #     return {"odoo_id": checklist_item.id} if checklist_item else {}

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
        """Map the backend id"""
        state = record.get("resolved")
        if state is True:
            return {"state": "done"}
        return {"state": "todo"}

    @mapping
    def exteral_id(self, record):
        """Map external Id"""
        # checklist_item = self.env["clickup.checklist.item"].search(
        #     [("external_id", "=", record.get("id"))]
        # )
        # if checklist_item:
        #     raise MappingError(_("checklist item already exist"))
        return {"external_id": record.get("id")}

    @mapping
    def backend_id(self, record):
        """Map backend Id"""
        return {"backend_id": self.backend_record.id}
