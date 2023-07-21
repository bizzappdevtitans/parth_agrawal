import base64
import logging

import requests

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.addons.connector.exception import MappingError

_logger = logging.getLogger(__name__)


class ResUsersImporter(Component):
    _name = "clickup.res.users.importer"
    _inherit = "clickup.importer"
    _apply_on = "clickup.res.users"


class ProjectProjectBatchImporter(Component):
    """Delay import of the records"""

    _name = "clickup.res.users.batch.importer"
    _inherit = "clickup.delayed.batch.importer"
    _apply_on = "clickup.res.users"

    def run(self, filters=None, force=False, job_options=None):
        """Run the synchronization"""

        records = self.backend_adapter.search(filters)

        for rec in [records]:
            rec = rec.get("user", {})
            external_id = rec.get(self.backend_adapter._clickup_ext_id_key)

            self._import_record(
                external_id, data=rec, force=force, job_options=job_options
            )


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
        login = record.get("id")
        user = self.env["res.users"].search(
            [("login", "=", login)],
            limit=1,
        )
        if not user:
            return {"login": login}
        else:
            raise MappingError(_("User Exist with same login details"))

    @mapping
    def email(self, record):
        """Map name"""
        return {"email": record.get("email")}

    @mapping
    def profile(self, record):
        """Map name"""
        picture_url = record.get("profilePicture")
        response = requests.get(picture_url, timeout=10)
        if response.status_code == 200:
            picture_data = response.content
            picture_base64 = base64.b64encode(picture_data)
            return {"image_1920": picture_base64}
