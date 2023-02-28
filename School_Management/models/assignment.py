from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime


class Assignment(models.Model):
    _name = "assignment.option"
    _inherit = "mail.thread"
    _description = "assignment model"
    _rec_name = "studentname"

    studentname = fields.Many2one(
        "student.profile", string="Student name", tracking=True
    )
    teachername = fields.Many2one(
        "teacher.profile", string="Teacher name", tracking=True
    )
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
        ],
        string="gender",
    )
    department = fields.Many2one(related="studentname.subject", string="department")
    subjectarts = fields.Selection(
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
    subjectscience = fields.Selection(
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
    subjectcommerce = fields.Selection(
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
    # duedate1 = duedate.strftime("%Y-%m-%d")
    note = fields.Text("Assigned task", tracking=True)
    Task = fields.Binary(string="Upload Answer", tracking=True)
    submit = fields.Boolean("approve?", tracking=True)
    Questions = fields.Binary("Questions", tracking=True)

    @api.onchange("studentname")
    def _onchange_gender(self):
        self.gender = self.studentname.gender

    # @api.model
    # def name_search(self, studentname, args=None, operator="ilike", limit=100):
    #     args = args or []
    #     recs = self.browse()
    #     if not recs:
    #         recs = self.search(
    #             ["|", ("name", operator, studentname), ("phone", operator, studentname)]
    #             + args,
    #             limit=limit,
    #         )
    #     return recs.name_get()

    today = fields.Date(string="Today's date", default=datetime.today(), readonly=True)
    # today1 = today.strftime(today, "%Y-%m-%d")

    # @api.depends("today1", "duedate1")
    # def check_date(self):
    #     for rec in self:
    #         if rec.today1 > rec.duedate:
    #             rec.Task = False
