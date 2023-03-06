from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Marksheet(models.Model):
    _name = "marksheet.option"
    _description = "marksheet model"
    _rec_name = "studentname"

    studentname = fields.Many2one("student.profile", string="studentname")

    schoolname = fields.Many2one(
        related="studentname.studentschoolname", string="school name"
    )

    rollno = fields.Integer(related="studentname.rollno", string="roll no")

    department = fields.Many2one(related="studentname.subject", string="Department")

    standard = fields.Selection(
        [("11th", "11TH"), ("12th", "12TH")], string="Select Class"
    )

    semester = fields.Selection(
        [("1st", "1st"), ("2nd", "2nd")], string="Select Semester"
    )

    geography = fields.Integer(string="Geography")
    history = fields.Integer(string="History")
    Economics = fields.Integer(string="Economics(A)")
    Politicalscience = fields.Integer(string="Political Science")
    Sociology = fields.Integer(string="Sociology")
    Philosophy = fields.Integer(string="Philosophy")
    Psychology = fields.Integer(string="Psychology")
    artstotal = fields.Integer(compute="_compute_arts_marks", string="Total Arts Marks")
    artspercentage = fields.Float(string="Arts Percentage", compute="_compute_percent_arts")
    artsgrade = fields.Char(string="Arts Grade", compute="_compute_grade_arts")
    artsresult = fields.Char(string="Arts result", compute="_compute_result_arts")

    biology = fields.Integer(string="Biology")
    chemistry = fields.Integer(string="Chemistry")
    mathemetics = fields.Integer(string="Mathemetics")
    Physics = fields.Integer(string="Physics")
    English = fields.Integer(string="English(S)")
    sciencetotal = fields.Integer(
        compute="_compute_science_marks", string="Total Science Marks"
    )
    sciencepercentage = fields.Float(
        string="Science Percentage", compute="_compute_percent_science"
    )
    sciencegrade = fields.Char(string="Science Grade", compute="_compute_grade_science")
    scienceresult = fields.Char(string="Science result", compute="_compute_result_science")

    accounts = fields.Integer(string="Accountancy")
    statistics = fields.Integer(string="statistics")
    Businessstudies = fields.Integer(string="Business Studies")
    Economics1 = fields.Integer(string="Economics(C)")
    English1 = fields.Integer(string="English(C)")
    commercetotal = fields.Integer(
        compute="_compute_commerce_marks", string="Total Commerce Marks"
    )
    commercepercentage = fields.Float(
        string="Commerce Percentage", compute="_compute_percent_commerce"
    )
    commercegrade = fields.Char(string="Commerce Grade", compute="_compute_grade_commerce")
    commerceresult = fields.Char(string="Commerce result", compute="_compute_result_commerce")

    @api.depends(
        "geography",
        "history",
        "Economics",
        "Politicalscience",
        "Sociology",
        "Philosophy",
        "Psychology",
    )
    def _compute_arts_marks(self):
        for record in self:
            record.artstotal = (
                record.geography
                + record.history
                + record.Economics
                + record.Politicalscience
                + record.Sociology
                + record.Philosophy
                + record.Psychology
            )

    @api.depends("artstotal")
    def _compute_percent_arts(self):
        for record in self:
            record.artspercentage = record.artstotal / 7
            return record.artspercentage

    @api.depends("artspercentage")
    def _compute_grade_arts(self):
        for record in self:
            if record.artspercentage >= 85.00:
                record.artsgrade = "A+"
            elif record.artspercentage >= 70.00 and record.artspercentage < 85.00:
                record.artsgrade = "A"
            elif record.artspercentage >= 60.00 and record.artspercentage < 70.00:
                record.artsgrade = "B+"
            elif record.artspercentage >= 50.00 and record.artspercentage < 60.00:
                record.artsgrade = "B"
            elif record.artspercentage >= 35.00 and record.artspercentage < 50.00:
                record.artsgrade = "C"
            else:
                record.artsgrade = "F"

    @api.depends("artspercentage")
    def _compute_result_arts(self):
        for record in self:
            if record.artspercentage >= 35.00:
                record.artsresult = "Congratulations! you are pass in exam"
            else:
                record.artsresult = "Sorry! you are fail in exam"

    @api.depends(
        "biology",
        "chemistry",
        "mathemetics",
        "Physics",
        "English",
    )
    def _compute_science_marks(self):
        for record in self:
            record.sciencetotal = (
                record.biology
                + record.chemistry
                + record.mathemetics
                + record.Physics
                + record.English
            )

    @api.depends("sciencetotal")
    def _compute_percent_science(self):
        for record in self:
            record.sciencepercentage = record.sciencetotal / 5
            return record.sciencepercentage

    @api.depends("sciencepercentage")
    def _compute_grade_science(self):
        for record in self:
            if record.sciencepercentage >= 85.00:
                record.sciencegrade = "A+"
            elif record.sciencepercentage >= 70.00 and record.sciencepercentage < 85.00:
                record.sciencegrade = "A"
            elif record.sciencepercentage >= 60.00 and record.sciencepercentage < 70.00:
                record.sciencegrade = "B+"
            elif record.sciencepercentage >= 50.00 and record.sciencepercentage < 60.00:
                record.sciencegrade = "B"
            elif record.sciencepercentage >= 35.00 and record.sciencepercentage < 50.00:
                record.sciencegrade = "C"
            else:
                record.sciencegrade = "F"

    @api.depends("sciencepercentage")
    def _compute_result_science(self):
        for record in self:
            if record.sciencepercentage >= 35.00:
                record.scienceresult = "Congratulations! you are pass in exam"
            else:
                record.scienceresult = "Sorry! you are fail in exam"

    @api.depends(
        "accounts",
        "statistics",
        "Businessstudies",
        "Economics1",
        "English1",
    )
    def _compute_commerce_marks(self):
        for record in self:
            record.commercetotal = (
                record.accounts
                + record.statistics
                + record.Businessstudies
                + record.Economics1
                + record.English1
            )

    @api.depends("commercetotal")
    def _compute_percent_commerce(self):
        for record in self:
            record.commercepercentage = record.commercetotal / 5
            return record.commercepercentage

    @api.depends("commercepercentage")
    def _compute_grade_commerce(self):
        for record in self:
            if record.commercepercentage >= 85.00:
                record.commercegrade = "A+"
            elif (
                record.commercepercentage >= 70.00 and record.commercepercentage < 85.00
            ):
                record.commercegrade = "A"
            elif (
                record.commercepercentage >= 60.00 and record.commercepercentage < 70.00
            ):
                record.commercegrade = "B+"
            elif (
                record.commercepercentage >= 50.00 and record.commercepercentage < 60.00
            ):
                record.commercegrade = "B"
            elif (
                record.commercepercentage >= 35.00 and record.commercepercentage < 50.00
            ):
                record.commercegrade = "C"
            else:
                record.commercegrade = "F"

    @api.depends("commercepercentage")
    def _compute_result_commerce(self):
        for record in self:
            if record.commercepercentage >= 35.00:
                record.commerceresult = "Congratulations! you are pass in exam"
            else:
                record.commerceresult = "Sorry! you are fail in exam"

    #########################################################

    @api.constrains("geography")
    def _check_geography(self):
        for record in self:
            if record.geography > 100 or record.geography < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in geography"
                )

    @api.constrains("history")
    def _check_history(self):
        for record in self:
            if record.history > 100 or record.history < 0:
                raise ValidationError("Marks should be in range of 0 to 100 in history")

    @api.constrains("Economics")
    def _check_Economics(self):
        for record in self:
            if record.Economics > 100 or record.Economics < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in Economics"
                )

    @api.constrains("Politicalscience")
    def _check_Politicalscience(self):
        for record in self:
            if record.Politicalscience > 100 or record.Politicalscience < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in Politicalscience"
                )

    @api.constrains("Sociology")
    def _check_Sociology(self):
        for record in self:
            if record.Sociology > 100 or record.Sociology < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in Sociology"
                )

    @api.constrains("Philosophy")
    def _check_Philosophy(self):
        for record in self:
            if record.Philosophy > 100 or record.Philosophy < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in Philosophy"
                )

    @api.constrains("Psychology")
    def _check_Psychology(self):
        for record in self:
            if record.Psychology > 100 or record.Psychology < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in Psychology"
                )

    @api.constrains("biology")
    def _check_biology(self):
        for record in self:
            if record.biology > 100 or record.biology < 0:
                raise ValidationError("Marks should be in range of 0 to 100 in biology")

    @api.constrains("chemistry")
    def _check_chemistry(self):
        for record in self:
            if record.chemistry > 100 or record.chemistry < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in chemistry"
                )

    @api.constrains("mathemetics")
    def _check_mathemetics(self):
        for record in self:
            if record.mathemetics > 100 or record.mathemetics < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in mathemetics"
                )

    @api.constrains("Physics")
    def _check_Physics(self):
        for record in self:
            if record.Physics > 100 or record.Physics < 0:
                raise ValidationError("Marks should be in range of 0 to 100 in Physics")

    @api.constrains("English")
    def _check_English(self):
        for record in self:
            if record.English > 100 or record.English < 0:
                raise ValidationError("Marks should be in range of 0 to 100 in English")

    @api.constrains("accounts")
    def _check_accounts(self):
        for record in self:
            if record.accounts > 100 or record.accounts < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in accounts"
                )

    @api.constrains("statistics")
    def _check_statistics(self):
        for record in self:
            if record.statistics > 100 or record.statistics < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in statistics"
                )

    @api.constrains("Businessstudies")
    def _check_Businessstudies(self):
        for record in self:
            if record.Businessstudies > 100 or record.Businessstudies < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in Businessstudies"
                )

    @api.constrains("Economics1")
    def _check_Economics1(self):
        for record in self:
            if record.Economics1 > 100 or record.Economics1 < 0:
                raise ValidationError(
                    "Marks should be in range of 0 to 100 in Economics"
                )

    @api.constrains("English1")
    def _check_English1(self):
        for record in self:
            if record.English1 > 100 or record.English1 < 0:
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
        if vals.get("reference_no", "New") == "New":
            vals["reference_no"] = (
                self.env["ir.sequence"].next_by_code("marksheet.option") or "New"
            )
        res = super(Marksheet, self).create(vals)
        return res
