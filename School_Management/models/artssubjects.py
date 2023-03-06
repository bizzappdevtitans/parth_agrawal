from odoo import fields, models, api


class ArtsSubjects(models.Model):
    _name = "subjects.arts"
    _description = "arts subject model"
    _rec_name = "artspart"

    artspart = fields.Selection(
        [
            ("geography", "Geography"),
            ("history", "History"),
            ("Economics", "Economics"),
            ("Politicalscience", "Politicalscience"),
            ("sociology", "Sociology"),
            ("philosophy", "Philosophy"),
            ("psychology", "Psychology"),
        ],
        string="Arts Subjects",
    )
