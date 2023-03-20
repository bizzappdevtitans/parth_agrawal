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

    mobile_number = fields.Char(related="studentname_id.phone", string="Mobile")
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
    submit_student_side = fields.Boolean(string="approved?", tracking=True)
    Questions = fields.Binary("Questions", tracking=True)
    today = fields.Date(string="Today's date", default=datetime.today(), readonly=True)

    alert_message = fields.Selection(
        [
            ("due_today", "Due date of assignment is today"),
            ("due_future", "Due date of assignment is comming soon"),
            ("due_past", "Due date of assignment is already passed"),
        ]
    )

    @api.onchange("studentname_id")
    def _onchange_gender(self):
        """The gender will change according to the selected student"""
        self.gender = self.studentname_id.gender

    @api.onchange("submit")
    def _onchange_submit(self):
        for assignment in self:
            assignment.submit_student_side = assignment.submit
            # return assignment.submit_student_side

    @api.model
    def test_cron_assignment(self):
        """Scheduled action that check assignment duedate of student and
        return co-responding field value if matched"""
        print("\n \n TESTING CRON JOB Assignment \n \n")
        equal = self.env["assignment.option"].search([("duedate", "=", "today")])
        greater = self.env["assignment.option"].search([("duedate", ">", "today")])
        lesser = self.env["assignment.option"].search([("duedate", "<", "today")])
        if equal:
            equal.write({"alert_message": "due_today"})

        if greater:
            greater.write({"alert_message": "due_future"})

        if lesser:
            lesser.write({"alert_message": "due_past"})

    def action_share_whatsapp(self):
        if not self.studentname_id.phone:
            raise ValidationError(("Mobile number not found"))
        message = "Hello *%s*, Your assignment is missing. due date is '''_%s_'''" % (self.studentname_id.name,self.duedate)
        whatsapp_api_url = (
            "https://web.whatsapp.com/send?phone="
            + self.mobile_number
            + "&text="
            + message
        )

        result = {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": whatsapp_api_url,
        }

        return result
