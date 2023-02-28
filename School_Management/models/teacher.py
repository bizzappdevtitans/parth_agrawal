from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re


class TeacherProfile(models.Model):
    _name = "teacher.profile"
    _description = "teacher profile model"

    tag = fields.Selection(
        [
            ("mr.", "Mr."),
            ("miss", "Miss"),
            ("mrs.", "Mrs."),
        ]
    )
    name = fields.Char("Name")
    image = fields.Binary("Image", store=True)
    email = fields.Char("Email")
    marriage = fields.Boolean("Are you married?")
    mobile = fields.Char("Mobile")
    status = fields.Selection(
        [
            ("less than 5 years", "Less than 5 years"),
            ("more than 5 years", "More than 5 years"),
        ],
        "Work Experience",
    )
    school_list = fields.Many2many(
        "school.profile", string="which schools have you taught?"
    )
    Redirect = fields.Reference(
        selection=[
            ("addmission.option", "percentage"),
            ("assignment.option", "Task"),
        ],
        string="Redirect To",
    )

    _sql_constraints = [
        ("email", "UNIQUE (email)", "Email ID already exist enter unique Email ID"),
    ]

    # @api.constrains("email")
    # def validate_email(self):
    #     for record in self:
    #         if (
    #             re.match(
    #                 "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$",
    #                 record.email,
    #             )
    #             == None
    #         ):
    #             raise ValidationError(
    #                 "Please Provide valid Email Address: %s" % record.email
    #             )
    #             return True

    @api.model
    def _name_search(
        self, name="", args=None, operator="like", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if name:
            args += [
                "|",
                "|",
                ("name", operator, name),
                ("email", operator, name),
                ("mobile", operator, name),
            ]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
