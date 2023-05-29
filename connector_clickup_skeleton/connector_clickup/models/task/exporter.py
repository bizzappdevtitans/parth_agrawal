import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class ProjectTaskExporter(Component):
    _name = "clickup.project.task.exporter"
    _inherit = "clickup.exporter"
    _apply_on = "clickup.project.tasks"

    def _has_to_skip(self):
        """prevent exporting return to everstox"""
        # if self.binding.is_return_picking:
        #     return True
        return

    def run(self, binding, record=None, *args, **kwargs):
        """Override Method to create the shipment for each picking
        with sale binding."""

        self.mapper.map_record(record)


class ProjectTaskDelayedBatchExporter(Component):
    """Delay import of the records"""

    _name = "clickup.project.task.batch.exporter"
    _inherit = "clickup.delayed.batch.exporter"
    _apply_on = "clickup.project.tasks"


class ProjectTaskImportMapper(Component):
    _name = "clickup.project.task.export.mapper"
    _inherit = "clickup.export.mapper"
    _apply_on = "clickup.project.tasks"
    _mapper_ext_key = "identifier"

    @mapping
    def name(self, record):
        name = record.name

        return {"name": name}

    @mapping
    def content(self, record):
        content = record.description

        return {"content": content}
