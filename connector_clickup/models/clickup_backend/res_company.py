from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    clickup_backend_id = fields.Many2one(
        comodel_name="clickup.backend",
        string="Default Clickup Backend",
    )
    # shop_instance_id = fields.Char(string="Everstox Shop Instance ID")
    # test_shop_instance_id = fields.Char(string="Staging Everstox Shop Instance ID")
