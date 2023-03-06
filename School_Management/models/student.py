from odoo import fields, models, api


class StudentProfile(models.Model):
    _name = "student.profile"
    _description = "profile model"

    name = fields.Char("student name")
    photo = fields.Binary("Photo", store=True)
    rollno = fields.Integer("rollno")
    subject = fields.Many2one("department.option", string="Field")

    rate = fields.Integer(related="subject.rate")
    dob = fields.Date("Date of Birth")
    phone = fields.Char("phone")
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
        ]
    )
    studentschoolname = fields.Many2one("school.profile", string="school name")
    tuition = fields.Integer(related="studentschoolname.tuition")
    library = fields.Integer(related="studentschoolname.library")
    transport = fields.Integer(related="studentschoolname.transport")
    stationary = fields.Integer(related="studentschoolname.stationary")
    security = fields.Integer(related="studentschoolname.security")
    admission = fields.Integer(related="studentschoolname.admission")
    other = fields.Integer(related="studentschoolname.other")
    # selectedsubsarts = fields.Many2many("subjects.arts",string="Arts subjects")
    # selectedsubsscience = fields.Many2many("subjects.science",string="Science subjects")
    # selectedsubscommerce = fields.Many2many("subjects.commerce",string="Commerce subjects")
    totalmarks = fields.Integer("Total marks")
    percentage = fields.Float("Last Exam percentage")
    signature = fields.Binary("Digital Signature")
    hobby = fields.Many2many("hobbies.selection", string="Hobbies")
    document = fields.Binary("Upload Documents")
    redirect = fields.Reference(
        selection=[
            ("school.profile", "name"),
            ("feedback.option", "priority"),
        ],
        string="Redirect To",
    )

    def action_school_profile(self):
        return

    addressofschool = fields.Text(
        related="studentschoolname.address", string="school address"
    )
    websiteofschool = fields.Char(
        related="studentschoolname.website", string="school website"
    )
    emailofschool = fields.Char(
        related="studentschoolname.email", string="school email"
    )
    phoneofschool = fields.Char(
        related="studentschoolname.phone", string="school phone"
    )

    marksheetcount = fields.Integer(compute="count_marksheet", string="Marksheet")
    feescount = fields.Integer(compute="count_fees", string="Fees")

    @api.depends("name")
    def count_marksheet(self):
        for record in self:
            record.marksheetcount = self.env["marksheet.option"].search_count(
                [("studentname", "=", self.name)]
            )

    def action_student_marksheet(self):
        return {
            "type": "ir.actions.act_window",
            "name": "name",
            "view_mode": "tree,form",
            "res_model": "marksheet.option",
            "domain": [("studentname", "=", self.name)],
            "context": "{'create': False}",
        }

    @api.depends("name")
    def count_fees(self):
        for record in self:
            record.feescount = self.env["fees.option"].search_count(
                [("studentname", "=", self.name)]
            )

    def action_fees_option(self):
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
        res = super(StudentProfile, self).default_get(fields)
        res["gender"] = "male"
        res["name"] = "Enter Student Name"
        return res

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
                ("phone", operator, name),
                ("subject", operator, name),
            ]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    def name_get(self):
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
        if vals.get("reference_no", "New") == "New":
            vals["reference_no"] = (
                self.env["ir.sequence"].next_by_code("student.profile") or "New"
            )
        res = super(StudentProfile, self).create(vals)
        return res

