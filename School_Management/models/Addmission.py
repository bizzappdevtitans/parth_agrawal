from odoo import fields, models, api
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import re


class Addmission(models.Model):
    _name = "addmission.option"
    _description = "new addmission model"

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("done", "Done"),
            ("cancel", "Cancel"),
        ],
        string="Form Status",
    )

    name = fields.Char(string="name", help="Enter Your Name")
    father = fields.Char("father name")
    mother = fields.Char("mother name")
    occupation_select = fields.Selection(
        [
            ("father", "Father"),
            ("mother", "Mother"),
        ],
        "Select Parent for Occupation",
    )
    occupation = fields.Char("occupation detail")
    pincode = fields.Integer("Pincode")
    photo = fields.Binary("Passportsize photo", store=True)
    standard = fields.Many2one("department.option", string="Stream")
    dob = fields.Date("Date of Birth")
    age = fields.Char("age", compute="_compute_age")
    phone = fields.Char("phone")
    email = fields.Char("Email Id")
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
        ]
    )
    address = fields.Text("address")
    problem = fields.Selection(
        [
            ("yes", "Yes"),
            ("no", "No"),
        ],
        "Any disability",
    )
    specify = fields.Char("specify disability if any(optional)*")

    schoolname = fields.Many2one("school.profile", "school name")
    studentcount = fields.Integer(string="existing students")

    percentage = fields.Float("Exam percentage", compute="_compute_percent")
    hobby = fields.Many2many("hobbies.selection", string="Hobbies")
    signature = fields.Binary("Digital Signature")
    document = fields.Binary(
        "Upload combined Document file(1.Aadhar card 2.Last standard marksheet 3.birth certificate etc.) "
    )

    @api.depends("dob")
    def _compute_age(self):
        for student in self:
            age = relativedelta(
                datetime.now().date(), fields.Datetime.from_string(student.dob)
            ).years
            student.age = str(age) + " Years"

    maths = fields.Integer("Maths marks")
    science = fields.Integer("Science marks")
    english = fields.Integer("English marks")
    HindiGujarati = fields.Integer("Hindi/Gujarati marks")
    total = fields.Integer("total marks", compute="_compute_marks")

    @api.depends("maths", "science", "english", "HindiGujarati")
    def _compute_marks(self):
        for record in self:
            record.total = (
                record.maths + record.science + record.english + record.HindiGujarati
            )

    @api.depends("total")
    def _compute_percent(self):
        for record in self:
            record.percentage = record.total / 4

    @api.constrains("maths")
    def _check_maths(self):
        for record in self:
            if record.maths > 100 or record.maths < 0:
                raise ValidationError("Marks should be in range of 0 to 100 in maths")

    @api.constrains("science")
    def _check_science(self):
        for record in self:
            if record.science > 100 or record.science < 0:
                raise ValidationError("Marks should be in range of 0 to 100 in science")

    @api.constrains("english")
    def _check_english(self):
        for record in self:
            if record.english > 100 or record.english < 0:
                raise ValidationError("Marks should be in range of 0 to 100 in english")

    @api.constrains("HindiGujarati")
    def _check_HindiGujarati(self):
        for record in self:
            if record.HindiGujarati > 100 or record.HindiGujarati < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in Hindi/Gujarati"
                )

    @api.constrains("phone")
    def _check_phone(self):
        for record in self:
            if len(record.phone) > 10 or len(record.phone) < 10:
                raise UserError("phone number must consist 10 digits")

    @api.onchange("schoolname")
    def _onchange_schoolname(self):
        self.studentcount = self.schoolname.studentcount

    _sql_constraints = [
        (
            "phone",
            "UNIQUE (phone)",
            "Phone number already exist in record try to add other phone number !",
        )
    ]

    _sql_constraints = [
        (
            "email",
            "UNIQUE (email)",
            "Email Id already exist in record try to add other Email Id !",
        )
    ]

    def unlink(self):
        if self.state == "done":
            raise ValidationError(
                "You can not delete the record which is in Done stage. To delete you need to change state from Done to Cancel"
            )
        elif self.state == "draft":
            raise ValidationError(
                "You can not delete the record which is in Draft stage. To delete you need to change state from Draft to Cancel"
            )
        return super(Addmission, self).unlink()

    def action_confirm(self):
        for rec in self:
            rec.state = "done"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancel"

    @api.model
    def create(self, vals):
        vals["state"] = "draft"
        return super(Addmission, self).create(vals)
