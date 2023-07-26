from odoo.addons.component.core import AbstractComponent


class BaseClickupConnectorComponent(AbstractComponent):
    """Base Clickup Connector Component
    All components of this connector should inherit from it.
    """

    _name = "base.clickup.connector"
    _inherit = "base.connector"
    _collection = "clickup.backend"
