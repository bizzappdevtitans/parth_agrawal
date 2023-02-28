from odoo import fields, models, api


class Department(models.Model):
    _name = "department.option"
    _description = "department model"
    _rec_name = "field"

    field = fields.Selection(
        [
            ("science", "Science"),
            ("commerce", "Commerce"),
            ("arts", "Arts"),
        ],
        "Select stream",
    )

    admission_student = fields.One2many(
        "addmission.option", "standard", string="Enrollment request"
    )

    currentstudent = fields.One2many(
        "student.profile", "subject", string="Enrolled Student"
    )

    enrolledstudentcount = fields.Integer(
        compute="_count_studentsold", string="Total Enrolled Student"
    )
    requeststudentcount = fields.Integer(
        compute="_count_studentsnew", string="Total Admission request"
    )

    # studentname=fields.Many2one("student.profile")

    api.depends("currentstudent")

    def _count_studentsold(self):
        for record in self:
            record.enrolledstudentcount = self.env["student.profile"].search_count(
                [("subject", "=", self.field)]
            )

    api.depends("admission_student")

    def _count_studentsnew(self):
        for record in self:
            record.requeststudentcount = self.env["addmission.option"].search_count(
                [("standard", "=", self.field)]
            )

    def action_student_profile(self):
        return {
            "type": "ir.actions.act_window",
            "name": "name",
            "view_mode": "tree,form",
            "res_model": "student.profile",
            "domain": [("subject", "=", self.field)],
            "context": "{'create': False}",
        }

    def action_addmission_option(self):
        return {
            "type": "ir.actions.act_window",
            "name": "name",
            "view_mode": "tree,form",
            "res_model": "addmission.option",
            "domain": [("standard", "=", self.field)],
            "context": "{'create': False}",
        }

    rate = fields.Integer(compute="fees_acordingdept", string="department fees")

    @api.depends("field")
    def fees_acordingdept(self):
        for record in self:
            if record.field == "science":
                record.rate = 5000
            elif record.field == "commerce":
                record.rate = 4000
            elif record.field == "arts":
                record.rate = 3000
