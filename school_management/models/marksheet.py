from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Marksheet(models.Model):
    """This model show the marksheet of student and can be created new marksheet in it"""

    _name = "marksheet.option"
    _description = "marksheet option model"
    _rec_name = "studentname_id"

    studentname_id = fields.Many2one("student.profile", string="studentname")

    schoolname_id = fields.Many2one(
        related="studentname_id.student_school_name_id", string="school name"
    )

    rollno = fields.Integer(related="studentname_id.rollno", string="roll no")

    department_id = fields.Many2one(related="studentname_id.subject_id", string="Department")

    standard = fields.Selection(
        [("11th", "11TH"), ("12th", "12TH")], string="Select Class"
    )

    semester = fields.Selection(
        [("1st", "1st"), ("2nd", "2nd")], string="Select Semester"
    )

    geography = fields.Integer(string="Geography")
    history = fields.Integer(string="History")
    economics_arts = fields.Integer(string="Economics(A)")
    political_science = fields.Integer(string="Political Science")
    sociology = fields.Integer(string="Sociology")
    philosophy = fields.Integer(string="Philosophy")
    psychology = fields.Integer(string="Psychology")
    artstotal = fields.Integer(compute="_compute_arts_marks", string="Total Arts Marks")
    arts_percentage = fields.Float(
        string="Arts Percentage", compute="_compute_percent_arts"
    )
    artsgrade = fields.Char(string="Arts Grade", compute="_compute_grade_arts")
    artsresult = fields.Char(string="Arts result", compute="_compute_result_arts")

    biology = fields.Integer(string="Biology")
    chemistry = fields.Integer(string="Chemistry")
    mathemetics = fields.Integer(string="Mathemetics")
    physics = fields.Integer(string="Physics")
    english_science = fields.Integer(string="English(S)")
    sciencetotal = fields.Integer(
        compute="_compute_science_marks", string="Total Science Marks"
    )
    science_percentage = fields.Float(
        string="Science Percentage", compute="_compute_percent_science"
    )
    sciencegrade = fields.Char(string="Science Grade", compute="_compute_grade_science")
    scienceresult = fields.Char(
        string="Science result", compute="_compute_result_science"
    )

    accounts = fields.Integer(string="Accountancy")
    statistics = fields.Integer(string="statistics")
    business_studies = fields.Integer(string="Business Studies")
    economics_commerce = fields.Integer(string="Economics(C)")
    english_commerce = fields.Integer(string="English(C)")
    commercetotal = fields.Integer(
        compute="_compute_commerce_marks", string="Total Commerce Marks"
    )
    commerce_percentage = fields.Float(
        string="Commerce Percentage", compute="_compute_percent_commerce"
    )
    commercegrade = fields.Char(
        string="Commerce Grade", compute="_compute_grade_commerce"
    )
    commerceresult = fields.Char(
        string="Commerce result", compute="_compute_result_commerce"
    )

    @api.depends(
        "geography",
        "history",
        "economics_arts",
        "political_science",
        "sociology",
        "philosophy",
        "psychology",
    )
    def _compute_arts_marks(self):
        """To compute the total marks for arts department students"""
        for marksheet in self:
            marksheet.artstotal = (
                marksheet.geography
                + marksheet.history
                + marksheet.economics_arts
                + marksheet.political_science
                + marksheet.sociology
                + marksheet.philosophy
                + marksheet.psychology
            )

    @api.depends("artstotal")
    def _compute_percent_arts(self):
        """To compute the percentage for arts subjects"""
        for marksheet in self:
            marksheet.arts_percentage = marksheet.artstotal / 7
            return marksheet.arts_percentage

    @api.depends("arts_percentage")
    def _compute_grade_arts(self):
        """To show the grade of student who is from arts department"""
        for marksheet in self:
            if marksheet.arts_percentage >= 85.00:
                marksheet.artsgrade = "A+"
            elif (
                marksheet.arts_percentage >= 70.00 and marksheet.arts_percentage < 85.00
            ):
                marksheet.artsgrade = "A"
            elif (
                marksheet.arts_percentage >= 60.00 and marksheet.arts_percentage < 70.00
            ):
                marksheet.artsgrade = "B+"
            elif (
                marksheet.arts_percentage >= 50.00 and marksheet.arts_percentage < 60.00
            ):
                marksheet.artsgrade = "B"
            elif (
                marksheet.arts_percentage >= 35.00 and marksheet.arts_percentage < 50.00
            ):
                marksheet.artsgrade = "C"
            else:
                marksheet.artsgrade = "F"

    @api.depends("arts_percentage")
    def _compute_result_arts(self):
        """To print message of pass or fail for arts department students"""
        for marksheet in self:
            if marksheet.arts_percentage >= 35.00:
                marksheet.artsresult = "Congratulations! you are pass in exam"
            else:
                marksheet.artsresult = "Sorry! you are fail in exam"

    @api.depends(
        "biology",
        "chemistry",
        "mathemetics",
        "physics",
        "english_science",
    )
    def _compute_science_marks(self):
        """To compute the total marks for science department students"""
        for marksheet in self:
            marksheet.sciencetotal = (
                marksheet.biology
                + marksheet.chemistry
                + marksheet.mathemetics
                + marksheet.physics
                + marksheet.english_science
            )

    @api.depends("sciencetotal")
    def _compute_percent_science(self):
        """To compute the percentage for science subjects"""
        for marksheet in self:
            marksheet.science_percentage = marksheet.sciencetotal / 5
            return marksheet.science_percentage

    @api.depends("science_percentage")
    def _compute_grade_science(self):
        """To show the grade of student who is from science department"""
        for marksheet in self:
            if marksheet.science_percentage >= 85.00:
                marksheet.sciencegrade = "A+"
            elif (
                marksheet.science_percentage >= 70.00
                and marksheet.science_percentage < 85.00
            ):
                marksheet.sciencegrade = "A"
            elif (
                marksheet.science_percentage >= 60.00
                and marksheet.science_percentage < 70.00
            ):
                marksheet.sciencegrade = "B+"
            elif (
                marksheet.science_percentage >= 50.00
                and marksheet.science_percentage < 60.00
            ):
                marksheet.sciencegrade = "B"
            elif (
                marksheet.science_percentage >= 35.00
                and marksheet.science_percentage < 50.00
            ):
                marksheet.sciencegrade = "C"
            else:
                marksheet.sciencegrade = "F"

    @api.depends("science_percentage")
    def _compute_result_science(self):
        """To print message of pass or fail for science department students"""
        for marksheet in self:
            if marksheet.science_percentage >= 35.00:
                marksheet.scienceresult = "Congratulations! you are pass in exam"
            else:
                marksheet.scienceresult = "Sorry! you are fail in exam"

    @api.depends(
        "accounts",
        "statistics",
        "business_studies",
        "economics_commerce",
        "english_commerce",
    )
    def _compute_commerce_marks(self):
        """To compute total of commerce subjects"""
        for marksheet in self:
            marksheet.commercetotal = (
                marksheet.accounts
                + marksheet.statistics
                + marksheet.business_studies
                + marksheet.economics_commerce
                + marksheet.english_commerce
            )

    @api.depends("commercetotal")
    def _compute_percent_commerce(self):
        """To find percentage of commerce subjects"""
        for marksheet in self:
            marksheet.commerce_percentage = marksheet.commercetotal / 5
            return marksheet.commerce_percentage

    @api.depends("commerce_percentage")
    def _compute_grade_commerce(self):
        """To show the grade of student who is from commerce department"""
        for marksheet in self:
            if marksheet.commerce_percentage >= 85.00:
                marksheet.commercegrade = "A+"
            elif (
                marksheet.commerce_percentage >= 70.00
                and marksheet.commerce_percentage < 85.00
            ):
                marksheet.commercegrade = "A"
            elif (
                marksheet.commerce_percentage >= 60.00
                and marksheet.commerce_percentage < 70.00
            ):
                marksheet.commercegrade = "B+"
            elif (
                marksheet.commerce_percentage >= 50.00
                and marksheet.commerce_percentage < 60.00
            ):
                marksheet.commercegrade = "B"
            elif (
                marksheet.commerce_percentage >= 35.00
                and marksheet.commerce_percentage < 50.00
            ):
                marksheet.commercegrade = "C"
            else:
                marksheet.commercegrade = "F"

    @api.depends("commerce_percentage")
    def _compute_result_commerce(self):
        """To print message of pass or fail for commerce department students"""
        for marksheet in self:
            if marksheet.commerce_percentage >= 35.00:
                marksheet.commerceresult = "Congratulations! you are pass in exam"
            else:
                marksheet.commerceresult = "Sorry! you are fail in exam"

    @api.constrains("geography")
    def _check_geography(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.geography > 100 or marksheet.geography < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in geography"
                )

    @api.constrains("history")
    def _check_history(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.history > 100 or marksheet.history < 0:
                raise ValidationError("Marks should be in range of 0 to 100 in history")

    @api.constrains("economics_arts")
    def _check_economics_arts(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.economics_arts > 100 or marksheet.economics_arts < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in Economics"
                )

    @api.constrains("political_science")
    def _check_political_science(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.political_science > 100 or marksheet.political_science < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in Politicalscience"
                )

    @api.constrains("sociology")
    def _check_sociology(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.sociology > 100 or marksheet.sociology < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in Sociology"
                )

    @api.constrains("philosophy")
    def _check_philosophy(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.philosophy > 100 or marksheet.philosophy < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in Philosophy"
                )

    @api.constrains("psychology")
    def _check_psychology(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.psychology > 100 or marksheet.psychology < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in Psychology"
                )

    @api.constrains("biology")
    def _check_biology(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.biology > 100 or marksheet.biology < 0:
                raise ValidationError("Marks should be in range of 0 to 100 in biology")

    @api.constrains("chemistry")
    def _check_chemistry(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.chemistry > 100 or marksheet.chemistry < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in chemistry"
                )

    @api.constrains("mathemetics")
    def _check_mathemetics(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.mathemetics > 100 or marksheet.mathemetics < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in mathemetics"
                )

    @api.constrains("physics")
    def _check_physics(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.physics > 100 or marksheet.physics < 0:
                raise ValidationError("Marks should be in range of 0 to 100 in Physics")

    @api.constrains("english_science")
    def _check_english_science(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.english_science > 100 or marksheet.english_science < 0:
                raise ValidationError("Marks should be in range of 0 to 100 in English")

    @api.constrains("accounts")
    def _check_accounts(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.accounts > 100 or marksheet.accounts < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in accounts"
                )

    @api.constrains("statistics")
    def _check_statistics(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.statistics > 100 or marksheet.statistics < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in statistics"
                )

    @api.constrains("business_studies")
    def _check_business_studies(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.business_studies > 100 or marksheet.business_studies < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in Businessstudies"
                )

    @api.constrains("economics_commerce")
    def _check_economics_commerce(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.economics_commerce > 100 or marksheet.economics_commerce < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in Economics"
                )

    @api.constrains("english_commerce")
    def _check_english_commerce(self):
        """check the upper bound and lower bound of the marks for the particular subject"""
        for marksheet in self:
            if marksheet.english_commerce > 100 or marksheet.english_commerce < 0:
                raise ValidationError("Marks should be in range of 0 to 100 in English")

    reference_no = fields.Char(
        string="Marksheet No",
        required=True,
        readonly=True,
        index=True,
        default=lambda self: ("New"),
    )

    @api.model
    def create(self, vals):
        """To generate sequence number for marksheet"""
        if vals.get("reference_no", "New") == "New":
            vals["reference_no"] = (
                self.env["ir.sequence"].next_by_code("marksheet.option") or "New"
            )
        res = super(Marksheet, self).create(vals)
        return res
