from odoo import fields, models


class SaleOrderInherit(models.Model):
    """To pass value from SO to DO , MO, PO, invoice ,project and task"""

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
        """This method helps to pass value from SO to invoice that is in Basic option"""
        invoice_dec = super(SaleOrderInherit, self)._prepare_invoice()
        invoice_dec["invoice_description"] = self.invoice_description
        return invoice_dec

    # def _get_new_picking_values(self):
    #     """This method helps to pass value from SO to delivery order"""
    #     picking_vals = super(SaleOrderInherit, self)._get_new_picking_values()
    #     picking_vals["delivery_description"] = self.delivery_description
    #     data = self.env["stock.picking"].search([])
    #     for move in data.move_lines:
    #         sale_line = move.sale_line_id
    #         if sale_line:
    #             move["weight"] = sale_line.weight
    #     return picking_vals

    def _prepare_analytic_account_data(self, prefix):
        """This method helps to pass value from SO to project and task"""
        values = super(SaleOrderInherit, self)._prepare_analytic_account_data(prefix)
        values["project_description"] = self.project_description
        values["task_description"] = self.task_description
        return values

    def _get_purchase_orders(self):
        """This method helps to pass value from SO to purchase order"""
        povalues = super(SaleOrderInherit, self)._get_purchase_orders()
        povalues["purchase_des"] = self.purchase_description
        print(povalues)
        return povalues
