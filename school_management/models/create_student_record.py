from odoo import fields, models, api


class CreateRecord(models.Model):
    """Give access to use ORM methods like create/update/unlink etc."""

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

    name_orm = fields.Char(
        compute="compute_action_browse_created_record", string="Browsed name"
    )
    rollno_orm = fields.Char(
        compute="compute_action_browse_created_record", string="Browsed roll no"
    )

    def action_insert_created_record(self):
        """The data inserted in create.record object will
        be added in student.profile object"""
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
    def compute_action_update_created_record(self):
        """The data firstly browsed and then updated in
        student.profile model"""
        for orm_record in self:
            student_dict1 = {
                "name": self.name,
                "photo": self.photo,
                "rollno": self.rollno,
                "dob": self.dob,
                "phone": self.phone,
                "gender": self.gender,
            }
        self.env["student.profile"].browse(orm_record.recid).write(student_dict1)

    @api.depends("recid")
    def compute_action_browse_created_record(self):
        """Browse the record and show name and roll no of student
        by taking their recid"""
        for orm_record in self:
            val1 = self.env["student.profile"]
            studentprofile = val1.browse(orm_record.recid)
            orm_record.name_orm = studentprofile.name
            orm_record.rollno_orm = studentprofile.rollno
            return [orm_record.name_orm, orm_record.rollno_orm]

    @api.depends("recid")
    def compute_action_unlink_created_record(self):
        """Delete record of student.profile model by taking recid"""
        for orm_record in self:
            self.env["student.profile"].browse(orm_record.recid).unlink()

    def action_search_created_record(self):
        """Show searched record in digits by using domain"""
        for orm_record in self:
            val = self.env["student.profile"]
            studentprofile = len(val.search([("gender", "=", "male")]))
            orm_record.searchlist = studentprofile
            return orm_record.searchlist

    searchlist = fields.Char(
        compute="action_search_created_record",
        string="searchlist(Domain is gender = male)",
    )
