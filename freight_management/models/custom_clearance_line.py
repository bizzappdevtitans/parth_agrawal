from werkzeug import urls
from odoo import api, fields, models


class CustomClearanceLine(models.Model):
    _name = "custom.clearance.line"
    _description = "Custom Clearance Line"

    name = fields.Char("Document Name")
    document = fields.Binary(string="Documents", store=True, attachment=True)
    line_id = fields.Many2one("custom.clearance")
