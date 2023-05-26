import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class ProjectProjectExporter(Component):
    _name = "clickup.project.project.exporter"
    _inherit = "clickup.exporter"
    _apply_on = "clickup.project.project"


class ProjectProjectDelayedBatchExporter(Component):
    """Delay import of the records"""

    _name = "clickup.project.project.batch.exporter"
    _inherit = "clickup.delayed.batch.exporter"
    _apply_on = "clickup.project.project"


class ProjectProjectImportMapper(Component):
    _name = "clickup.project.project.export.mapper"
    _inherit = "clickup.export.mapper"
    _apply_on = "clickup.project.project"
    _mapper_ext_key = "identifier"

    @mapping
    def name(self, record):
        name = record.name

        return {"name": name}

    @mapping
    def content(self, record):
        content = record.description

        return {"content": content}
