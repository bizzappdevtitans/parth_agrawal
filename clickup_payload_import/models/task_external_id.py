from odoo import fields, models


class ProjectExternalId(models.Model):
    _inherit = "project.task"
    _description = "inherited task model"

    external_id = fields.Char(string="External Id", readonly=True)
