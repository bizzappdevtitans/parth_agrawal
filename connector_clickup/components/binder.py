from odoo.addons.component.core import Component


class ClickupModelBinder(Component):
    _name = "clickup.binder"
    _inherit = ["base.binder", "base.clickup.connector"]
    _apply_on = [
        "clickup.project.project",
        "clickup.project.task",
        "clickup.project.task.type",
    ]
