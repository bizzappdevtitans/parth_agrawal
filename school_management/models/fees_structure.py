from odoo import fields, models, api


class FeesStructure(models.Model):
    """Show fees structure to the students according to the department and school"""

    _name = "fees.option"
    _description = "fees option model"
    _rec_name = "studentname"

    studentname = fields.Many2one("student.profile", string="studentname")
    student_image = fields.Binary(related="studentname.photo", string="photo")
    phoneno = fields.Char(related="studentname.phone", string="Mobile no")
    schoolname = fields.Many2one(
        related="studentname.student_school_name_id", string="school name"
    )

    address_school = fields.Text(
        related="studentname.school_address", string="school address"
    )
    website_school = fields.Char(
        related="studentname.school_website", string="school website"
    )
    email_school = fields.Char(
        related="studentname.school_email", string="school email"
    )
    phone_school = fields.Char(
        related="studentname.school_phone", string="school phone"
    )

    department = fields.Many2one(related="studentname.subject_id", string="Department")

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

    grandtotal = fields.Integer(
        string="grand total", compute="_compute_grand_totalfees"
    )

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
    def _compute_grand_totalfees(self):
        """Compute the grand total of fees by adding different types of fees"""
        for fees in self:
            fees.grandtotal = (
                fees.department_fees
                + fees.tuition
                + fees.library
                + fees.transport
                + fees.stationary
                + fees.security
                + fees.admission
                + fees.other
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
        """Helps to generate sequence for fees receipt"""
        if vals.get("reference_no", "New") == "New":
            vals["reference_no"] = (
                self.env["ir.sequence"].next_by_code("fees.option") or "New"
            )
        res = super(FeesStructure, self).create(vals)
        return res
