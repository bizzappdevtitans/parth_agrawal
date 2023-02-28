from odoo import fields, models, api


class FeesStructure(models.Model):
    _name = "fees.option"
    _description = "fees option model"
    _rec_name = "studentname"

    studentname = fields.Many2one("student.profile", string="studentname")
    studentimage = fields.Binary(related="studentname.photo", string="photo")
    phoneno = fields.Char(related="studentname.phone", string="Mobile no")
    schoolname = fields.Many2one(
        related="studentname.studentschoolname", string="school name"
    )

    addressofschool = fields.Text(
        related="studentname.addressofschool", string="school address"
    )
    websiteofschool = fields.Char(
        related="studentname.websiteofschool", string="school website"
    )
    emailofschool = fields.Char(
        related="studentname.emailofschool", string="school email"
    )
    phoneofschool = fields.Char(
        related="studentname.phoneofschool", string="school phone"
    )

    department = fields.Many2one(related="studentname.subject", string="Department")

    department_fees = fields.Integer(related="studentname.rate", string="deparment fee")

    tuition = fields.Integer(related="studentname.tuition", string="tuition fee")
    library = fields.Integer(related="studentname.library", string="library fee")
    transport = fields.Integer(related="studentname.transport", string="transport fee")
    stationary = fields.Integer(related="studentname.stationary", string="stationary")
    security = fields.Integer(related="studentname.security", string="security")
    admission = fields.Integer(
        related="studentname.admission", string="admission form fee"
    )
    other = fields.Integer(related="studentname.other", string="other")

    grandtotal = fields.Integer(string="grand total", compute="_grand_totalfees")

    @api.depends(
        "department_fees",
        "tuition",
        "library",
        "transport",
        "stationary",
        "security",
        "admission",
        "other",
    )
    def _grand_totalfees(self):
        for record in self:
            record.grandtotal = (
                record.department_fees
                + record.tuition
                + record.library
                + record.transport
                + record.stationary
                + record.security
                + record.admission
                + record.other
            )

    reference_no = fields.Char(
        string="Receipt No",
        required=True,
        readonly=True,
        index=True,
        default=lambda self: ("New"),
    )

    @api.model
    def create(self, vals):
        if vals.get("reference_no", "New") == "New":
            vals["reference_no"] = (
                self.env["ir.sequence"].next_by_code("fees.option") or "New"
            )
        res = super(FeesStructure, self).create(vals)
        return res
