from odoo import fields, models


class ProjectExternalId(models.Model):
    _inherit = "project.project"
    _description = "inherited project model"

    external_id = fields.Char(string="External Id", readonly=True)
