from odoo import fields, models

from odoo.addons.component.core import Component


class ClickupProjectTasks(models.Model):
    _name = "clickup.project.tasks"
    _inherits = {"project.task": "odoo_id"}
    _inherit = ["clickup.model"]
    _description = "Clickup project.tasks binding model"

    odoo_id = fields.Many2one(
        "project.task", string="Task", required=True, ondelete="restrict"
    )


class ProjectTask(models.Model):
    _inherit = "project.task"
    _description = "Inherited project.task model"

    clickup_bind_ids = fields.One2many(
        "clickup.project.tasks",
        "odoo_id",
        string="Clickup Backend ID",
        readonly=True,
    )
    external_id = fields.Char(
        related="clickup_bind_ids.external_id",
        readonly=True,
    )
    backend_id = fields.Many2one(
        "clickup.backend",
        related="clickup_bind_ids.backend_id",
        string="Clickup Backend",
        readonly=True,
    )
    api_token_data = fields.Char(
        string="API token",
        readonly=True,
    )
    created_at = fields.Datetime(string="Created At", readonly=True)

    updated_at = fields.Datetime(string="Updated At", readonly=True)
    disable_button = fields.Boolean(default=False, readonly=False)


class TaskAdapter(Component):
    _name = "clickup.project.task.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.project.tasks"
    _akeneo_model = "clickup.project.tasks"
    _akeneo_ext_id_key = "id"


#     def _call(self, method, arguments, http_method=None, storeview=None):
#         try:
#             return super(TaskAdapter, self)._call(
#                 method, arguments, http_method=http_method, storeview=storeview
#             )
#         except xmlrpc.client.Fault as err:
#             # this is the error in the Magento API
#             # when the customer does not exist
#             if err.faultCode == 102:
#                 raise TaskAdapter
#             else:
#                 raise

#     def read(self, external_id, attributes=None, storeview=None):
#         """Returns the information of a record"""
