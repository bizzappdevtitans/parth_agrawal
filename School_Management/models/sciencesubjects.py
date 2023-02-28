from odoo import fields, models, api


class ScienceSubjects(models.Model):
    _name = "subjects.science"
    _description = "science subject model"
    _rec_name = "sciencepart"

    sciencepart = fields.Selection(
        [
            ("biology", "Biology"),
            ("chemistry", "Chemistry"),
            ("mathemetics", "Mathemetics"),
            ("Physics", "Physics"),
            ("English", "English"),
        ],
        string="Science Subjects",
    )
