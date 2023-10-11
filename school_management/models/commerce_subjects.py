from odoo import fields, models, api


class CommerceSubjects(models.Model):
    """Give the list of commerce subjects"""

    _name = "subjects.commerce"
    _description = "commerce subject model"
    _rec_name = "commerce_part"

    commerce_part = fields.Selection(
        [
            ("accounts", "Accountancy"),
            ("statistics", "statistics"),
            ("Businessstudies", "Business Studies"),
            ("Economics", "Economics"),
            ("English", "English"),
        ],
        string="Commerce Subjects",
    )
