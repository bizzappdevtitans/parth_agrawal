from odoo import fields, models, api


class AccountAnalitic(models.Model):
    """To relate the field and pass value from SO to project and Task """
    _inherit = "account.analytic.account"

    project_description = fields.Char(string="Project Description")
    task_description = fields.Char(string="Task Description")


class ProjectInherit(models.Model):
    """To Pass the value from SO to Project"""
    _inherit = "project.project"

    analytic_account_id = fields.Many2one("account.analytic.account")
    project_description = fields.Char(
        string="Project Description",
        related="analytic_account_id.project_description",
    )
    task_description = fields.Char(
        string="Task Description",
        related="analytic_account_id.task_description",
    )
