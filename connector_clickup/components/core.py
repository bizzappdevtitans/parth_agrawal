from odoo.addons.component.core import AbstractComponent


class BaseClickupConnectorComponent(AbstractComponent):
    """Base Clickup Connector Component
    All components of this connector should inherit from it.
    """

    _name = "base.clickup.connector"
    _inherit = "base.connector"
    _collection = "clickup.backend"

    def queue_job_description(self):
        model = self.model._name
        model_parts = model.split(".")
        model_name = " ".join(part.title() for part in model_parts[1:])
        model_name = " ".join(dict.fromkeys(model_name.split()))
        return model_name
