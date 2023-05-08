from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = "project.project"

    clickup_bind_ids = fields.One2many(
        "clickup.project.project", "odoo_id", string="Clickup Backend ID"
    )
    external_id = fields.Char(related="clickup_bind_ids.external_id")


class ProjectTask(models.Model):
    _inherit = "project.task"

    clickup_bind_ids = fields.One2many(
        "clickup.project.tasks", "odoo_id", string="Clickup Backend ID"
    )


# class ProjectProject(models.Model):
#     _inherit = "project.task.type"

#     clickup_bind_ids = fields.One2many(
#         "clickup.backend", "clickup_bind_id", string="Clickup Backend ID"
#     )
