from odoo import fields, models, api


class ScienceSubjects(models.Model):
    """Give the list of science subjects"""

    _name = "subjects.science"
    _description = "science subject model"
    _rec_name = "science_part"

    science_part = fields.Selection(
        [
            ("biology", "Biology"),
            ("chemistry", "Chemistry"),
            ("mathemetics", "Mathemetics"),
            ("Physics", "Physics"),
            ("English", "English"),
        ],
        string="Science Subjects",
    )
