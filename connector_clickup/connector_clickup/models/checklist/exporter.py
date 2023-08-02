import logging

from odoo.osv import expression

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class TaskChecklistExporter(Component):
    _name = "clickup.task.checklist.exporter"
    _inherit = "clickup.exporter"
    _apply_on = "clickup.task.checklist"


class TaskChecklistDelayedBatchExporter(Component):
    """Delay import of the records"""

    _name = "clickup.task.checklist.batch.exporter"
    _inherit = "clickup.delayed.batch.exporter"
    _apply_on = "clickup.task.checklist"

    def run(self, filters=None, job_options=None):
        """Run the synchronization"""
        filters = filters or {}
        domain = expression.OR(
            [
                [("clickup_bind_ids", "=", False)],
                [("clickup_backend_id", "=", self.backend_record.id)],
            ]
        )
        records = self.env["task.checklist"].search(domain)
        for record in records:
            self._export_record(record, job_options=job_options)


class ChecklistItemImportMapper(Component):
    _name = "clickup.task.checklist.export.mapper"
    _inherit = "clickup.export.mapper"
    _apply_on = "clickup.task.checklist"
    _mapper_ext_key = "identifier"
    # _map_child_fallback = "clickup.map.child.exporter"

    # children = [
    #     (
    #         "items",
    #         "clickup_checklist_item_ids",
    #         "clickup.checklist.item",
    #     ),
    # ]

    @mapping
    def name(self, record):
        """Mapped name"""
        return {"name": record.name}

    @mapping
    def task_id(self, record):
        """Mapped task_id"""
        return {"task_id": record.clickup_bind_ids.external_id}
