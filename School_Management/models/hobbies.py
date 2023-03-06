from odoo import fields, models


class Hobbies(models.Model):
    _name = "hobbies.selection"
    _description = "hobbies model"
    _rec_name = "hobbyselection"

    hobbyselection = fields.Selection(
        [
            ("reading", "Reading"),
            ("dancing", "Dancing"),
            ("singing", "Singing"),
            ("cooking", "Cooking"),
            ("driving", "Driving"),
            ("playing", "Playing"),
        ],
        "Hobby Selection",
    )

    studentlist = fields.Many2many("student.profile", string="studentlist")
