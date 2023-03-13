from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime


class Assignment(models.Model):
    """This will show the assignment that is assigned to the students"""

    _name = "assignment.option"
    _inherit = "mail.thread"
    _description = "assignment option model"
    _rec_name = "studentname_id"

    studentname_id = fields.Many2one(
        "student.profile", string="Student name", tracking=True
    )
    teachername_id = fields.Many2one(
        "teacher.profile", string="Teacher name", tracking=True
    )
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
        ],
        string="gender",
    )
    department_id = fields.Many2one(
        related="studentname_id.subject_id", string="department"
    )
    subject_arts = fields.Selection(
        [
            ("geography", "Geography"),
            ("history", "History"),
            ("Economics", "Economics"),
            ("Politicalscience", "Politicalscience"),
            ("sociology", "Sociology"),
            ("philosophy", "Philosophy"),
            ("psychology", "Psychology"),
        ],
        string="Arts Subjects",
        tracking=True,
    )
    subject_science = fields.Selection(
        [
            ("biology", "Biology"),
            ("chemistry", "Chemistry"),
            ("mathemetics", "Mathemetics"),
            ("Physics", "Physics"),
            ("English", "English"),
        ],
        string="Science Subjects",
        tracking=True,
    )
    subject_commerce = fields.Selection(
        [
            ("accounts", "Accountancy"),
            ("statistics", "statistics"),
            ("Businessstudies", "Business Studies"),
            ("Economics", "Economics"),
            ("English", "English"),
        ],
        string="Commerce Subjects",
        tracking=True,
    )
    duedate = fields.Date("Due date to upload", tracking=True)
    note = fields.Text("Assigned task", tracking=True)
    Task = fields.Binary(string="Upload Answer", tracking=True)
    submit = fields.Boolean("approve?", tracking=True)
    submit_student_side = fields.Boolean(
        string="approved?", tracking=True
    )
    Questions = fields.Binary("Questions", tracking=True)
    today = fields.Date(string="Today's date", default=datetime.today(), readonly=True)

    @api.onchange("studentname_id")
    def _onchange_gender(self):
        """The gender will change according to the selected student"""
        self.gender = self.studentname_id.gender

    @api.onchange("submit")
    def _onchange_submit(self):
        for assignment in self:
            assignment.submit_student_side = assignment.submit
            # return assignment.submit_student_side
