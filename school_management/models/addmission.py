from odoo import fields, models, api
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import re


class Addmission(models.Model):
    """This model take new student's information for admission
    and also uses status bar on form view"""

    _name = "addmission.option"
    _description = "addmission option model"

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
    standard_id = fields.Many2one("department.option", string="Stream")
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

    schoolname_id = fields.Many2one("school.profile", "school name")
    studentcount = fields.Integer(string="existing students")

    percentage = fields.Float("Exam percentage", compute="_compute_percent")
    hobby_ids = fields.Many2many("hobbies.selection", string="Hobbies")
    signature = fields.Binary("Digital Signature")
    document = fields.Binary(
        "Upload combined Document file(1.Aadhar card 2.Last standard marksheet 3.birth certificate etc.) "
    )

    maths = fields.Integer("Maths marks")
    science = fields.Integer("Science marks")
    english = fields.Integer("English marks")
    hindi_gujarati = fields.Integer("Hindi/Gujarati marks")
    total = fields.Integer("total marks", compute="_compute_marks")

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

    @api.depends("dob")
    def _compute_age(self):
        """Compute the age by taking dob from user"""
        for addmission in self:
            age = relativedelta(
                datetime.now().date(), fields.Datetime.from_string(addmission.dob)
            ).years
            addmission.age = str(age) + " Years"

    @api.depends("maths", "science", "english", "hindi_gujarati")
    def _compute_marks(self):
        """Compute the total marks by taking all subjects marks"""
        for admission in self:
            admission.total = (
                admission.maths
                + admission.science
                + admission.english
                + admission.hindi_gujarati
            )

    @api.depends("total")
    def _compute_percent(self):
        """Compute the percentage by taking total marks"""
        for admission in self:
            admission.percentage = admission.total / 4

    @api.constrains("maths")
    def _check_maths(self):
        """Check upper and lower bound of inputed marks"""
        for admission in self:
            if admission.maths > 100 or admission.maths < 0:
                raise ValidationError("Marks should be in range of 0 to 100 in maths")

    @api.constrains("science")
    def _check_science(self):
        """Check upper and lower bound of inputed marks"""
        for admission in self:
            if admission.science > 100 or admission.science < 0:
                raise ValidationError("Marks should be in range of 0 to 100 in science")

    @api.constrains("english")
    def _check_english(self):
        """Check upper and lower bound of inputed marks"""
        for admission in self:
            if admission.english > 100 or admission.english < 0:
                raise ValidationError("Marks should be in range of 0 to 100 in english")

    @api.constrains("hindi_gujarati")
    def _check_hindi_gujarati(self):
        """Check upper and lower bound of inputed marks"""
        for admission in self:
            if admission.hindi_gujarati > 100 or admission.hindi_gujarati < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in Hindi/Gujarati"
                )

    @api.constrains("phone")
    def _check_phone(self):
        """Check the length of inputed mobile number"""
        for admission in self:
            if len(admission.phone) > 10 or len(admission.phone) < 10:
                raise UserError("Phone number must consist 10 digits")

    @api.onchange("schoolname_id")
    def _onchange_schoolname(self):
        """By changing school name the student count field
        will be dynamically change"""
        self.studentcount = self.schoolname_id.studentcount

    def unlink(self):
        """User cannot delete the record if the state is in Done or Draft stage"""
        for admission in self:
            if admission.state == "done":
                raise ValidationError(
                    "You can not delete the record which is in Done stage. To delete you need to change state from Done to Cancel"
                )
            elif admission.state == "draft":
                raise ValidationError(
                    "You can not delete the record which is in Draft stage. To delete you need to change state from Draft to Cancel"
                )
        return super(Addmission, self).unlink()

    def action_confirm(self):
        for addmission in self:
            addmission.state = "done"

    def action_cancel(self):
        for addmission in self:
            addmission.state = "cancel"

    @api.model
    def create(self, vals):
        vals["state"] = "draft"
        return super(Addmission, self).create(vals)
