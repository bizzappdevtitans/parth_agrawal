from odoo import fields, models
from datetime import datetime


class Attendance(models.Model):
    '''Thish model give basic facility to record the attendence of student'''
    _name = "attendance.option"
    _description = "Attendance option model"
    _rec_name = "date"

    schoolname_id = fields.Many2one("school.profile", string="School Name")
    studentlist_ids = fields.One2many(related="schoolname_id.students_id", string="students list")
    date = fields.Date(string="Today's date", default=datetime.today())
    student_ids = fields.Many2many("student.profile", string="Present Student")
