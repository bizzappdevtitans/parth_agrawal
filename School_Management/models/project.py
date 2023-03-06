from odoo import fields, models, api


# class Analytic(models.Model):
#     _inherit = "account.analytic.account"

#     sale_order_ids = fields.One2many(
#         "sale.order.project_id", string="Sale orders", store=True
#     )
#     project_task_description = fields.Char(string="Project/Task Description")


class AccountAnalitic(models.Model):
    _inherit = "account.analytic.account"

    project_description = fields.Char(string="Project Description")
    task_description = fields.Char(string="Task Description")

class ProjectInherit(models.Model):
    _inherit = "project.project"

    # sale_id = fields.Many2one("sale.order")
    analytic_account_id = fields.Many2one("account.analytic.account")
    project_description = fields.Char(
        string="Project Description",
        related="analytic_account_id.project_description",
    )
    task_description = fields.Char(
        string="Task Description",
        related="analytic_account_id.task_description",
    )

# related="analytic_account_id.sale_order_ids.project_task_description",


# ,related="sale_id.project_task_description"
