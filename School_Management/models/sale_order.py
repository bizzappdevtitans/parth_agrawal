from odoo import fields, models, api


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    project_id = fields.Many2one("project.project", "project_id")

    feesstatus = fields.Selection(
        [
            ("paid", "Paid"),
            ("unpaid", "Unpaid"),
        ],
        string="Payment Status",
    )

    delivery_description = fields.Char("Delivery Description")
    invoice_description = fields.Char("Invoice Description")
    project_description = fields.Char(string="Project Description")
    task_description = fields.Char(string="Task Description")

    def _prepare_invoice(self):
        invoice_dec = super(SaleOrderInherit, self)._prepare_invoice()
        invoice_dec["invoice_description"] = self.invoice_description
        return invoice_dec

    def _get_new_picking_values(self):
        picking_vals = super(SaleOrderInherit, self)._get_new_picking_values()
        picking_vals["delivery_description"] = self.delivery_description
        return picking_vals

    def _prepare_analytic_account_data(self, prefix):
        values = super(SaleOrderInherit, self)._prepare_analytic_account_data(prefix)
        print("before")
        values["project_description"] = self.project_description
        values["task_description"] = self.task_description
        print("after")
        return values

    # def _timesheet_create_task_prepare_values(self, project_id):
    #     values = super(SaleOrderInherit, self)._timesheet_create_task_prepare_values(
    #         project_id
    #     )
    #     values.write({"project_task_description": self.project_task_description})
    #     return values

    # def action_confirm(self):
    #     res = super(SaleOrderInherit, self).action_confirm()
    #     for order in self:
    #         if order.project_id:
    #             order.project_id.project_task_description = (
    #                 order.project_task_description
    #             )
    #         for task in order.project_id.task_ids:
    #             task.order.project_id = order.order.project_id

    #     return res


###########################################################################################

# def _prepare_picking_vals(self):
#     picking_vals = super(SaleOrderInherit, self)._prepare_picking_vals()
#     picking_vals["delivery_description"] = self.delivery_description
#     return picking_vals

# def create(self, delivery_description):
#     picking_vals = super(SaleOrderInherit, self).create(delivery_description)
#     picking_vals["delivery_description"] = self.delivery_description
#     return picking_vals

# def _check_entire_pack(self):
#     picking_vals = super(SaleOrderInherit, self)._check_entire_pack()
#     picking_vals["delivery_description"] = self.delivery_description
#     return picking_vals

# def _put_in_pack(self):
#     picking_vals = super(SaleOrderInherit, self)._put_in_pack()
#     picking_vals["delivery_description"] = self.delivery_description
#     return picking_vals

# def _get_show_allocation(self):
#     picking_vals = super(SaleOrderInherit, self)._get_show_allocation()
#     picking_vals["delivery_description"] = self.delivery_description
#     return picking_vals

# def _assign_picking(self):
#     picking_vals = super(SaleOrderInherit, self)._assign_picking()
#     picking_vals["delivery_description"] = self.delivery_description
#     return picking_vals

# def _prepare_procurement_values(self):
#     picking_vals = super(SaleOrderInherit, self)._prepare_procurement_values()
#     picking_vals["delivery_description"] = self.delivery_description
#     return picking_vals


# def action_confirm(self):

#     res = super(SaleOrderInherit, self).action_confirm()

#     for addin in self.picking_ids:

#         addin.write({"delivery_description": self.delivery_description})

#     return res
