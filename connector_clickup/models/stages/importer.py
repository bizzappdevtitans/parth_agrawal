import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.exceptions import ValidationError
from odoo import _


# from odoo.addons import queue_job

_logger = logging.getLogger(__name__)


class ProjectTaskTypeImporter(Component):
    _name = "clickup.project.task.type.importer"
    _inherit = "clickup.importer"
    _apply_on = "clickup.project.task.type"


class ProjectTaskTypeBatchImporter(Component):
    """Delay import of the records"""

    _name = "clickup.project.task.type.batch.importer"
    _inherit = "clickup.delayed.batch.importer"
    _apply_on = "clickup.project.task.type"

    def run(self, filters=None, force=False):
        """Run the synchronization"""

        records = self.backend_adapter.search(filters)

        for record in records:
            tasks = record.get("tasks", [])
            for task in tasks:
                external_id = task.get(self.backend_adapter._clickup_ext_id_key)

                self._import_record(external_id, data=task, force=force)


class ProjectTaskTypeImportMapper(Component):
    _name = "clickup.project.task.type.import.mapper"
    _inherit = "clickup.import.mapper"
    _apply_on = "clickup.project.task.type"

    @only_create
    @mapping
    def odoo_id(self, record):
        """Getting product based on the SKU."""
        result = record.get("status").get("status")
        test = self.env["project.task.type"].search([("name", "=", result)])
        if not test:
            binder = self.binder_for(model="clickup.project.task.type")
            odoo_id = binder.to_internal(
                record.get("status").get("status"), unwrap=True
            )
            if not odoo_id:
                return {}
            return {"odoo_id": odoo_id.id}

    @mapping
    def name(self, record):
        try:
            result = record.get("status").get("status")
            # task_name = record.get("name")
            # test = self.env["project.task.type"].search([("name", "=", result)])

            return {"name": result}

        except ValidationError as ve:
            raise ValidationError(
                _("result = This Stage will be skipped as it already exist"), ve
            )

    @mapping
    def external_id(self, record):
        """#T-02383 Mapped external id"""
        external_id = record.get("status")
        test = self.env["project.task.type"].search([("external_id", "=", external_id)])
        if not test:
            return {"external_id": external_id}

    @mapping
    def backend_id(self, record):
        """Mapped the backend id"""
        result = record.get("status")
        test = self.env["project.task.type"].search([("external_id", "=", result)])
        if not test:
            data = self.backend_record.id

            return {"backend_id": data}
