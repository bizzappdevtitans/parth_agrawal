from odoo import fields, models, api


class StudentProfile(models.Model):
    """Give details of students"""

    _name = "student.profile"
    _description = "student profile model"

    name = fields.Char("student name")
    photo = fields.Binary("Photo", store=True)
    rollno = fields.Integer("rollno")
    subject_id = fields.Many2one("department.option", string="Field")

    rate = fields.Integer(related="subject_id.rate")
    dob = fields.Date("Date of Birth")
    phone = fields.Char("phone")
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
        ]
    )
    student_school_name_id = fields.Many2one("school.profile", string="school name")
    tuition = fields.Integer(related="student_school_name_id.tuition")
    library = fields.Integer(related="student_school_name_id.library")
    transport = fields.Integer(related="student_school_name_id.transport")
    stationary = fields.Integer(related="student_school_name_id.stationary")
    security = fields.Integer(related="student_school_name_id.security")
    admission = fields.Integer(related="student_school_name_id.admission")
    other = fields.Integer(related="student_school_name_id.other")

    totalmarks = fields.Integer("Total marks")
    percentage = fields.Float("Last Exam percentage")
    signature = fields.Binary("Digital Signature")
    hobby_ids = fields.Many2many("hobbies.selection", string="Hobbies")
    document = fields.Binary("Upload Documents")
    redirect = fields.Reference(
        selection=[
            ("school.profile", "name"),
            ("feedback.option", "priority"),
        ],
        string="Redirect To",
    )

    def action_school_profile(self):
        """To return smart button details from school.profile model"""
        return

    school_address = fields.Text(
        related="student_school_name_id.address", string="school address"
    )
    school_website = fields.Char(
        related="student_school_name_id.website", string="school website"
    )
    school_email = fields.Char(
        related="student_school_name_id.email", string="school email"
    )
    school_phone = fields.Char(
        related="student_school_name_id.phone", string="school phone"
    )

    marksheetcount = fields.Integer(
        compute="_compute_count_marksheet", string="Marksheet"
    )
    feescount = fields.Integer(compute="_compute_count_fees", string="Fees")

    @api.depends("name")
    def _compute_count_marksheet(self):
        """To count total marksheet for particular student"""
        for student in self:
            student.marksheetcount = self.env["marksheet.option"].search_count(
                [("studentname_id", "=", self.name)]
            )

    def action_student_marksheet(self):
        """To return smart button details from marksheet.option model"""
        return {
            "type": "ir.actions.act_window",
            "name": "name",
            "view_mode": "tree,form",
            "res_model": "marksheet.option",
            "domain": [("studentname_id", "=", self.name)],
            "context": "{'create': False}",
        }

    @api.depends("name")
    def _compute_count_fees(self):
        """To count total fees receipt for particular student"""
        for student in self:
            student.feescount = self.env["fees.option"].search_count(
                [("studentname", "=", self.name)]
            )

    def action_fees_option(self):
        """To return smart button details from fees.option model"""
        return {
            "type": "ir.actions.act_window",
            "name": "name",
            "view_mode": "tree,form",
            "res_model": "fees.option",
            "domain": [("studentname", "=", self.name)],
            "context": "{'create': False}",
        }

    attendance = fields.Many2one("attendance.option")

    @api.model
    def default_get(self, fields):
        """Show male as delfault choice selection when creating new student"""
        res = super(StudentProfile, self).default_get(fields)
        res["gender"] = "male"
        res["name"] = "Enter Student Name"
        return res

    @api.model
    def _name_search(
        self, name="", args=None, operator="like", limit=100, name_get_uid=None
    ):
        """Give option to search student by using other field values"""
        args = list(args or [])
        if name:
            args += [
                "|",
                "|",
                ("name", operator, name),
                ("phone", operator, name),
                ("subject_id", operator, name),
            ]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    def name_get(self):
        """To append id of student record"""
        result = []
        for rec in self:
            name = "[" + str(rec.id) + "]" + rec.name
            result.append((rec.id, name))
        return result

    reference_no = fields.Char(
        string="Reference No",
        required=True,
        readonly=True,
        index=True,
        default=lambda self: ("New"),
    )

    @api.model
    def create(self, vals):
        """To generate sequence number for student record"""
        if vals.get("reference_no", "New") == "New":
            vals["reference_no"] = (
                self.env["ir.sequence"].next_by_code("student.profile") or "New"
            )
        res = super(StudentProfile, self).create(vals)
        return res

    @api.model
    def test_cron(self):
        print("\n \n TESTING CRON JOB \n \n")
        data = self.env["student.profile"].search([("dob", "=", fields.Date.today())]).name_get()
        print("\t\t there is somone's birthday today...", data)
        # data1 = data.name_get()
        # print("\t\t there is somone's birthday today...", data1)
