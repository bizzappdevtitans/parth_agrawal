from odoo import fields, models, api


class Department(models.Model):
    """Show department and student list that associated with it"""

    _name = "department.option"
    _description = "department option model"
    _rec_name = "field"

    field = fields.Selection(
        [
            ("science", "Science"),
            ("commerce", "Commerce"),
            ("arts", "Arts"),
        ],
        "Select stream",
    )

    admission_student_ids = fields.One2many(
        "addmission.option", "standard_id", string="Enrollment request"
    )

    current_student_ids = fields.One2many(
        "student.profile", "subject_id", string="Enrolled Student"
    )

    enrolled_student_count = fields.Integer(
        compute="_count_studentsold", string="Total Enrolled Student"
    )
    request_student_count = fields.Integer(
        compute="_count_studentsnew", string="Total Admission request"
    )

    def _count_studentsold(self):
        """Count student that already studying for that department"""
        for department in self:
            department.enrolled_student_count = self.env["student.profile"].search_count(
                [("subject_id", "=", self.field)]
            )

    def _count_studentsnew(self):
        """Count student that applied for admission for that department"""
        for department in self:
            department.request_student_count = self.env["addmission.option"].search_count(
                [("standard_id", "=", self.field)]
            )

    def action_student_profile(self):
        """Used for smart button for existing student list"""
        return {
            "type": "ir.actions.act_window",
            "name": "name",
            "view_mode": "tree,form",
            "res_model": "student.profile",
            "domain": [("subject_id", "=", self.field)],
            "context": "{'create': False}",
        }

    def action_addmission_option(self):
        """Used for smart button for new student admission"""
        return {
            "type": "ir.actions.act_window",
            "name": "name",
            "view_mode": "tree,form",
            "res_model": "addmission.option",
            "domain": [("standard_id", "=", self.field)],
            "context": "{'create': False}",
        }

    rate = fields.Integer(
        compute="_compute_fees_acordingdept", string="department fees"
    )

    @api.depends("field")
    def _compute_fees_acordingdept(self):
        """Fees will be show according to the related department of the student"""
        for department in self:
            if department.field == "science":
                department.rate = 5000
            elif department.field == "commerce":
                department.rate = 4000
            elif department.field == "arts":
                department.rate = 3000
