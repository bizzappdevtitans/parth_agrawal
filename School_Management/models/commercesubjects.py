from odoo import fields, models, api


class CommerceSubjects(models.Model):
    _name = "subjects.commerce"
    _description = "commerce subject model"
    _rec_name = "commercepart"

    commercepart = fields.Selection(
        [
            ("accounts", "Accountancy"),
            ("statistics", "statistics"),
            ("Businessstudies", "Business Studies"),
            ("Economics", "Economics"),
            ("English", "English"),
        ],
        string="Commerce Subjects",
    )
