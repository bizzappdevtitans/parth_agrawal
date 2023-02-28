from odoo import fields, models
from datetime import datetime


class Attendance(models.Model):
    _name = "attendance.option"
    _description = "Attendance model"
    _rec_name = "date"

    schoolname = fields.Many2one("school.profile", string="School Name")
    studentlist = fields.One2many(related="schoolname.students", string="students list")
    date = fields.Date(string="Today's date", default=datetime.today())
    student = fields.Many2many("student.profile", string="Present Student")
