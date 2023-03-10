from odoo import fields, models


class Hobbies(models.Model):
    """Show the list of different hobbies"""
    _name = "hobbies.selection"
    _description = "hobbies selection model"
    _rec_name = "hobby_selection"

    hobby_selection = fields.Selection(
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

    studentlist_ids = fields.Many2many("student.profile", string="studentlist")
