from odoo import fields, models


class CreateDataWizard(models.TransientModel):
    """To create new wizard view to create assignment"""
    _name = "create.data.wizard"
    _description = "create data using wizard"

    student_name_id = fields.Many2one("student.profile", string="Student Name")
    note = fields.Text("Personal Note")
    date = fields.Date("Due date")

    def action_on_click_create(self):
        """This is useful to pass the value from wizard to assignment.option model"""
        values = {
            "studentname_id": self.student_name_id.id,
            "duedate": self.date,
            "note": self.note,
        }
        assignment_rec = self.env["assignment.option"].create(values)
        print("assignment Id=", assignment_rec.id)
        """The below dictionary ensure that form view will
        be open automatically"""
        data = {
            "name": ("assignment option"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "assignment.option",
            "res_id": assignment_rec.id,
        }
        return data
        # "target": "new",(to show in wizard as form)
