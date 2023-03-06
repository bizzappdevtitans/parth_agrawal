from odoo import fields, models, api


class CreateRecord(models.Model):
    _name = "create.record"
    _description = "create record model"

    name = fields.Char("student name")
    photo = fields.Binary("Photo", store=True)
    rollno = fields.Integer("rollno")

    dob = fields.Date("Date of Birth")
    phone = fields.Char("phone")
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
        ]
    )
    recid = fields.Integer(string="Record Browse/delete(enter ID)")

    name1 = fields.Char(compute="action_browse_created_record", string="Browsed name")
    rollno1 = fields.Char(
        compute="action_browse_created_record", string="Browsed roll no"
    )

    def action_insert_created_record(self):
        student_dict = {
            "name": self.name,
            "photo": self.photo,
            "rollno": self.rollno,
            "dob": self.dob,
            "phone": self.phone,
            "gender": self.gender,
        }
        self.env["student.profile"].create(student_dict)

    @api.depends("recid")
    def action_update_created_record(self):
        for rec in self:
            student_dict1 = {
                "name": self.name,
                "photo": self.photo,
                "rollno": self.rollno,
                "dob": self.dob,
                "phone": self.phone,
                "gender": self.gender,
            }
        self.env["student.profile"].browse(rec.recid).write(student_dict1)

    @api.depends("recid")
    def action_browse_created_record(self):
        for rec in self:
            val1 = self.env["student.profile"]
            studentprofile = val1.browse(rec.recid)
            rec.name1 = studentprofile.name
            rec.rollno1 = studentprofile.rollno
            # rec.val = val1
            # print(val1)
            # print(name1)
            # print(rollno)
            return [rec.name1, rec.rollno1]

    @api.depends("recid")
    def action_unlink_created_record(self):
        for rec in self:
            self.env["student.profile"].browse(rec.recid).unlink()

    def action_search_created_record(self):
        for rec in self:
            val = self.env["student.profile"]
            studentprofile = len(val.search([("gender", "=", "male")]))
            rec.searchlist = studentprofile
            return rec.searchlist

    searchlist = fields.Char(
        compute="action_search_created_record",
        string="searchlist(Domain is gender = male)",
    )
