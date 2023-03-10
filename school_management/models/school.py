from odoo import fields, models, api
from odoo.exceptions import ValidationError


class SchoolProfile(models.Model):
    """This model show the detail of school"""
    _name = "school.profile"
    _description = "school profile model"
    _rec_name = "name"

    name = fields.Selection(
        [
            ("Delhi Public School", "Delhi Public School"),
            ("Poddar International School", "Poddar International School"),
            ("Saint Ann's High School", "Saint Ann's High School"),
            ("Sakar English School", "Sakar English School"),
            ("Shanti Asiatic School", "Shanti Asiatic School"),
            ("N.M. High School", "N.M. High School"),
        ],
        "School Name",
    )
    simage = fields.Binary("Image", store=True)
    website = fields.Char("Official Website")
    email = fields.Char("email")
    phone = fields.Char("phone")
    department = fields.Boolean("addmission Open?")
    address = fields.Text("Address")
    reviewer_id = fields.One2many("feedback.option", "Schoolname_id")
    teacher_ids = fields.Many2many("teacher.profile", string="TeacherList")
    students_id = fields.One2many("student.profile", "student_school_name_id")
    admission_form_id = fields.Reference(
        selection=[
            ("department.option", "admission_student_ids"),
        ],
        string="Department",
    )

    studentcount = fields.Integer(compute="_compute_count_students", string="Student count")

    @api.depends("name")
    def _compute_count_students(self):
        """To find the student who study in particular school"""
        for school in self:
            school.studentcount = self.env["student.profile"].search_count(
                [("student_school_name_id", "=", self.name)]
            )

    def action_student_profile(self):
        """To give smart button view for student list"""
        return {
            "type": "ir.actions.act_window",
            "name": "name",
            "view_mode": "tree",
            "res_model": "student.profile",
            "domain": [("student_school_name_id", "=", self.name)],
            "context": "{'create': False}",
        }

    @api.ondelete(at_uninstall=False)
    def _check_enrollment(self):
        """Stop user from deleting record of school that consist students"""
        for school in self:
            if school.students_id:
                raise ValidationError(
                    "you cannot delete this school from record that consist students in it"
                )

    tuition = fields.Integer(compute="_compute_different_fees")
    library = fields.Integer(compute="_compute_different_fees")
    transport = fields.Integer(compute="_compute_different_fees")
    stationary = fields.Integer(compute="_compute_different_fees")
    security = fields.Integer(compute="_compute_different_fees")
    admission = fields.Integer(compute="_compute_different_fees")
    other = fields.Integer(compute="_compute_different_fees")

    @api.depends("name")
    def _compute_different_fees(self):
        """To compute different fees for different schools"""
        for school in self:
            if school.name == "Delhi Public School":
                school.tuition = 11500
                school.library = 3200
                school.transport = 5300
                school.stationary = 2000
                school.security = 1000
                school.admission = 500
                school.other = 1100
            elif school.name == "Poddar International School":
                school.tuition = 10000
                school.library = 2100
                school.transport = 4000
                school.stationary = 1500
                school.security = 1300
                school.admission = 400
                school.other = 1000
            elif school.name == "Saint Ann's High School":
                school.tuition = 13000
                school.library = 3100
                school.transport = 5000
                school.stationary = 4000
                school.security = 2000
                school.admission = 700
                school.other = 1500
            elif school.name == "Sakar English School":
                school.tuition = 9000
                school.library = 1150
                school.transport = 2170
                school.stationary = 1700
                school.security = 800
                school.admission = 200
                school.other = 500
            elif school.name == "Shanti Asiatic School":
                school.tuition = 11000
                school.library = 900
                school.transport = 3000
                school.stationary = 2700
                school.security = 2000
                school.admission = 900
                school.other = 1190
            elif school.name == "N.M. High School":
                school.tuition = 5000
                school.library = 400
                school.transport = 2050
                school.stationary = 1700
                school.security = 3000
                school.admission = 500
                school.other = 2000

    @api.model
    def _name_search(
        self, name="", args=None, operator="like", limit=100, name_get_uid=None
    ):
        """Search name with using other field values"""
        args = list(args or [])
        if name:
            args += [
                "|",
                "|",
                ("name", operator, name),
                ("website", operator, name),
                ("email", operator, name),
            ]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
