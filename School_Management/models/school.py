from odoo import fields, models, api
from odoo.exceptions import ValidationError


class SchoolProfile(models.Model):
    _name = "school.profile"
    _description = "profile model"
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
    teacher_list = fields.Many2many("teacher.profile", string="TeacherList")
    students = fields.One2many("student.profile", "studentschoolname")
    admissionform = fields.Reference(
        selection=[
            ("department.option", "admission_student"),
        ],
        string="Department",
    )

    studentcount = fields.Integer(compute="count_students", string="Student count")

    @api.depends("name")
    def count_students(self):
        for record in self:
            record.studentcount = self.env["student.profile"].search_count(
                [("studentschoolname", "=", self.name)]
            )

    def action_student_profile(self):
        return {
            "type": "ir.actions.act_window",
            "name": "name",
            "view_mode": "tree",
            "res_model": "student.profile",
            "domain": [("studentschoolname", "=", self.name)],
            "context": "{'create': False}",
        }

    @api.ondelete(at_uninstall=False)
    def _check_enrollment(self):
        for record in self:
            if record.students:
                raise ValidationError(
                    "you cannot delete this school from record that consist students in it"
                )

    tuition = fields.Integer(compute="different_fees")
    library = fields.Integer(compute="different_fees")
    transport = fields.Integer(compute="different_fees")
    stationary = fields.Integer(compute="different_fees")
    security = fields.Integer(compute="different_fees")
    admission = fields.Integer(compute="different_fees")
    other = fields.Integer(compute="different_fees")

    @api.depends("name")
    def different_fees(self):
        for record in self:
            if record.name == "Delhi Public School":
                record.tuition = 11500
                record.library = 3200
                record.transport = 5300
                record.stationary = 2000
                record.security = 1000
                record.admission = 500
                record.other = 1100
            elif record.name == "Poddar International School":
                record.tuition = 10000
                record.library = 2100
                record.transport = 4000
                record.stationary = 1500
                record.security = 1300
                record.admission = 400
                record.other = 1000
            elif record.name == "Saint Ann's High School":
                record.tuition = 13000
                record.library = 3100
                record.transport = 5000
                record.stationary = 4000
                record.security = 2000
                record.admission = 700
                record.other = 1500
            elif record.name == "Sakar English School":
                record.tuition = 9000
                record.library = 1150
                record.transport = 2170
                record.stationary = 1700
                record.security = 800
                record.admission = 200
                record.other = 500
            elif record.name == "Shanti Asiatic School":
                record.tuition = 11000
                record.library = 900
                record.transport = 3000
                record.stationary = 2700
                record.security = 2000
                record.admission = 900
                record.other = 1190
            elif record.name == "N.M. High School":
                record.tuition = 5000
                record.library = 400
                record.transport = 2050
                record.stationary = 1700
                record.security = 3000
                record.admission = 500
                record.other = 2000

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
                ("website", operator, name),
                ("email", operator, name),
            ]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
