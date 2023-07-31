from odoo.addons.component.core import Component


class ClickupModelBinder(Component):
    """
    Bind records and give odoo/clickup ids correspondence
    Binding models are models called ``clickup.{normal_model}``,
    like ``clickup.project.project``.
    They are ``_inherits`` of the normal models and contains
    the clickup ID, the ID of the clickup Backend and the additional
    fields belonging to the clickup instance.
    """

    _name = "clickup.binder"
    _inherit = ["base.binder", "base.clickup.connector"]
    _apply_on = [
        "clickup.project.project",
        "clickup.project.task",
        "clickup.project.task.type",
        "clickup.task.checklist",
        "clickup.checklist.item",
    ]
