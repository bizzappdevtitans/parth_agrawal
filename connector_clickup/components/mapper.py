from odoo.addons.component.core import AbstractComponent


class ClickupImportMapper(AbstractComponent):
    _name = "clickup.import.mapper"
    _inherit = ["base.clickup.connector", "base.import.mapper"]
    _usage = "import.mapper"


class ClickupExportMapper(AbstractComponent):
    _name = "clickup.export.mapper"
    _inherit = ["base.clickup.connector", "base.export.mapper"]
    _usage = "export.mapper"
