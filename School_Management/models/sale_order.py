from odoo import fields, models


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
    purchase_description = fields.Char(string="Purchase order description")
    manufacturing_description = fields.Char(string="Manufacturing description")

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
        values["project_description"] = self.project_description
        values["task_description"] = self.task_description
        return values

    def _get_purchase_orders(self):
        povalues = super(SaleOrderInherit, self)._get_purchase_orders()
        povalues["purchase_des"] = self.purchase_description
        print(povalues)
        return povalues

    # def _prepare_purchase_order(self, company_id, origins, values):
    #     values1 = super(SaleOrderInherit, self)._prepare_purchase_order(
    #         company_id, origins, values
    #     )
    #     values1.update({"purchase_description": self.purchase_description})
    #     print(values1)
    #     return values1

    # def action_create_purchase_order(self):
    #     povalues = super(SaleOrderInherit, self).action_create_purchase_order()
    #     povalues.create({"purchase_description" : self.purchase_description})
    #     return povalues


##
# def _prepare_purchase_order(self):
#     values1 = super(SaleOrderInherit, self)._prepare_purchase_order()
#     values1["purchase_description"] = self.purchase_description
#     return values1

# def _get_purchase_orders(self):
#     values = super(SaleOrderInherit, self)._get_purchase_orders()
#     values.create({"purchase_description": self.purchase_description})
#     return values

# def _action_confirm(self):
#     result = super(SaleOrderInherit, self)._action_confirm()
#     for result in self:
#         result["purchase_description"] = self.purchase_description
#     return result

# def _purchase_service_generation(self):
#     print("inside inherited method")
#     POvalues = super(SaleOrderInherit, self)._purchase_service_generation()
#     POvalues["purchase_description"] = self.purchase_description
#     return POvalues

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

##################################################################
# def _prepare_subcontract_mo_vals(self):
#     POvalues = super(SaleOrderInherit, self)._prepare_subcontract_mo_vals()
#     POvalues["purchase_description"] = self.purchase_description
#     return POvalues

#############

# class StockRule(models.Model):
#     _inherit = "stock.rule"

# sale_reference_id = fields.Many2one('sale.order')
# purchase_description = fields.Char(
#     string="Purchase order description", related="sale_reference_id.purchase_description"
# )
# print(purchase_description)

# def _prepare_purchase_order(self, company_id, origins, values):
#     values1 = super(StockRule, self)._prepare_purchase_order(
#         company_id, origins, values
#     )
#     values1["purchase_des"] = self.sale_reference_id.purchase_description
#     print(values1)
#     return values1

# def _make_po_get_domain(self, company_id, values, partner):
#     values1 = super(StockRule, self)._make_po_get_domain(
#        company_id, values, partner
#     )
#     values1["purchase_des"] = values.get('purchase_description')
#     print(values1)
#     return values1

# def _push_prepare_move_copy_values(self, move_to_copy, new_date):
#     values1 = super(StockRule, self)._push_prepare_move_copy_values(
#         move_to_copy, new_date
#     )
#     values1["purchase_des"] = self.purchase_description
#     print(values1)
#     return values1
