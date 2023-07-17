import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

_logger = logging.getLogger(__name__)


class ResUsersImportMapper(Component):
    _name = "clickup.res.users.import.mapper"
    _inherit = "clickup.import.mapper"
    _apply_on = "clickup.res.users"

    @only_create
    @mapping
    def odoo_id(self, record):
        """Creating odoo id"""

        user = self.get_binding(record, model=self._apply_on, value="id")

        if not user:
            return {}
        return {"odoo_id": user.id}

    @mapping
    def name(self, record):
        """Map name"""
        return {"name": record.get("username")}

    @mapping
    def login(self, record):
        """Map name"""
        return {"login": record.get("id")}

    @mapping
    def email(self, record):
        """Map name"""
        return {"email": record.get("email")}
