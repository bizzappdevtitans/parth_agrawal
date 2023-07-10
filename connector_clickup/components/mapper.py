from odoo.addons.component.core import AbstractComponent


class ClickupImportMapper(AbstractComponent):
    _name = "clickup.import.mapper"
    _inherit = ["base.clickup.connector", "base.import.mapper"]
    _usage = "import.mapper"

    def _get_binding_values(self, record, model=None, value=None):
        """Create binding"""
        binder = self.binder_for(model)
        binding = binder.to_internal(record.get(value), unwrap=True)
        return binding


class ClickupExportMapper(AbstractComponent):
    _name = "clickup.export.mapper"
    _inherit = ["base.clickup.connector", "base.export.mapper"]
    _usage = "export.mapper"
