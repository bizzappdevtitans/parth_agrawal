from odoo import fields, models


class Calendar(models.Model):
    _name = "calendar.option"
    _description = "calendar model"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("name")
    sub = fields.Char("subject")
    event = fields.Text("description")
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
