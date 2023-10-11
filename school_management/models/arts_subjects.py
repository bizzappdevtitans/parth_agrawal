from odoo import fields, models, api


class ArtsSubjects(models.Model):
    '''Give the list of Arts subjects'''
    _name = "subjects.arts"
    _description = "arts subject model"
    _rec_name = "arts_part"

    arts_part = fields.Selection(
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
