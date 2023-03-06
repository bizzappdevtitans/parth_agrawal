from odoo import fields, models


class CreateDataWizard(models.TransientModel):
    _name = "create.data.wizard"
    _description = "create data using wizard"

    name = fields.Many2one("student.profile", string="Student Name")
    note = fields.Text("Personal Note")
    date = fields.Date("Due date")

    # def action_on_click_create(self):
    #     print("\n\nhello ! here after clicking on create at wizard\n\n")

    def action_on_click_create(self):
        # print("\n\nhello ! here after clicking on create at wizard\n\n")
        values = {
            "studentname": self.name.id,
            "duedate": self.date,
            "note": self.note,
        }
        assignment_rec = self.env["assignment.option"].create(values)
        print("assignment Id=", assignment_rec.id)
        data = {
            "name": ("assignment option"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "assignment.option",
            "res_id": assignment_rec.id,
        }
        return data
        # "target": "new",(to show in wizard as form)
