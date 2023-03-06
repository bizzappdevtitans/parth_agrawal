from odoo import fields, models


class Feedback(models.Model):
    _name = "feedback.option"
    _description = "feedback model"

    badges = fields.Selection(
        [
            ("mr.", "Mr."),
            ("miss", "Miss"),
            ("mrs.", "Mrs."),
        ],
        default="mr.",
    )
    name = fields.Char("Your name")
    Schoolname_id = fields.Many2one("school.profile")
    Schoolphone = fields.Char(related="Schoolname_id.phone", string="School phone")
    subject = fields.Char("Subject")
    note = fields.Text("note")
    priority = fields.Selection(
        [
            ("0", "review not given"),
            ("1", "poor"),
            ("2", "Bad"),
            ("3", "Average"),
            ("4", "good"),
            ("5", "Excellent"),
        ],
        "Appreciation",
        default="0",
    )
    date = fields.Date("Date")
