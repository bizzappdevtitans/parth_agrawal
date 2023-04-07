from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class FreightOrder(models.Model):
    """This model is main model that create freight order"""
    _name = "freight.order"
    _description = "Freight Order"

    name = fields.Char("Name", default="New", readonly=True)
    shipper_id = fields.Many2one(
        "res.partner", "Shipper", required=True, help="Shipper's Details"
    )
    consignee_id = fields.Many2one(
        "res.partner", "Consignee", help="Details of consignee"
    )
    type = fields.Selection(
        [("import", "Import"), ("export", "Export")],
        "Import/Export",
        required=True,
        help="Type of freight operation",
    )
    transport_type = fields.Selection(
        [("land", "Land"), ("air", "Air"), ("water", "Water")],
        "Transport",
        help="Type of transportation",
        required=True,
    )
    land_type = fields.Selection(
        [("ltl", "LTL"), ("ftl", "FTL")],
        "Land Shipping",
        help="Types of shipment movement involved in Land",
    )
    water_type = fields.Selection(
        [("fcl", "FCL"), ("lcl", "LCL")],
        "Water Shipping",
        help="Types of shipment movement involved in Water",
    )
    order_date = fields.Date(
        string="Date", default=fields.Date.today(), help="Date of order"
    )
    loading_port_id = fields.Many2one(
        "freight.port",
        string="Loading Port",
        required=True,
        help="Loading port of the freight order",
    )
    discharging_port_id = fields.Many2one(
        "freight.port",
        string="Discharging Port",
        required=True,
        help="Discharging port of freight order",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submit", "Submitted"),
            ("confirm", "Confirmed"),
            ("invoice", "Invoiced"),
            ("done", "Done"),
            ("cancel", "Cancel"),
        ],
        default="draft",
    )
    clearance = fields.Boolean("Clearance")
    clearance_count = fields.Integer(compute="compute_count")
    invoice_count = fields.Integer(compute="compute_count")
    total_order_price = fields.Float("Total", compute="_compute_total_order_price")
    total_volume = fields.Float("Total Volume", compute="_compute_total_order_price")
    total_weight = fields.Float("Total Weight", compute="_compute_total_order_price")
    order_ids = fields.One2many("freight.order.line", "order_id")
    route_ids = fields.One2many("freight.order.routes.line", "route_id")
    total_route_sale = fields.Float("Total Sale", compute="_compute_total_route_cost")
    service_ids = fields.One2many("freight.order.service", "line_id")
    total_service_sale = fields.Float(
        "Service Total Sale", compute="_compute_total_service_cost"
    )
    agent_id = fields.Many2one(
        "res.partner", "Agent", required=True, help="Details of agent"
    )
    expected_date = fields.Date("Expected Date")
    track_ids = fields.One2many("freight.track", "track_id")
    note = fields.Text(string="Note")
    current = fields.Date(default=datetime.today())

    @api.constrains("expected_date")
    def _check_date(self):
        """check expected date to reach to be current of future date"""
        for freight in self:
            if freight.expected_date < freight.current:
                raise ValidationError("Expected date must not be past date")

    @api.constrains("consignee_id")
    def _check_consignee(self):
        """check shipper and consignee must no be same"""
        for freight in self:
            if freight.shipper_id == freight.consignee_id:
                raise ValidationError("Shipper and Consignee should be different")

    @api.depends("order_ids.total_price", "order_ids.volume", "order_ids.weight")
    def _compute_total_order_price(self):
        """Computing the price of the order"""
        for freight in self:
            freight.total_order_price = sum(freight.order_ids.mapped("total_price"))
            freight.total_volume = sum(freight.order_ids.mapped("volume"))
            freight.total_weight = sum(freight.order_ids.mapped("weight"))

    @api.depends("route_ids.sale")
    def _compute_total_route_cost(self):
        """Computing the total cost of route operation"""
        for freight in self:
            freight.total_route_sale = sum(freight.route_ids.mapped("sale"))

    @api.depends("service_ids.total_sale")
    def _compute_total_service_cost(self):
        """Computing the total cost of services"""
        for freight in self:
            freight.total_service_sale = sum(freight.service_ids.mapped("total_sale"))

    @api.model
    def create(self, vals):
        """Create Sequence"""
        sequence_code = "freight.order.sequence"
        vals["name"] = self.env["ir.sequence"].next_by_code(sequence_code)
        return super(FreightOrder, self).create(vals)

    def create_custom_clearance(self):
        """Create custom clearance"""
        clearance = self.env["custom.clearance"].create(
            {
                "name": "CC - " + self.name,
                "freight_id": self.id,
                "date": self.order_date,
                "loading_port_id": self.loading_port_id.id,
                "discharging_port_id": self.discharging_port_id.id,
                "agent_id": self.agent_id.id,
            }
        )
        result = {
            "name": "action.name",
            "type": "ir.actions.act_window",
            "views": [[False, "form"]],
            "target": "current",
            "res_id": clearance.id,
            "res_model": "custom.clearance",
        }
        self.clearance = True
        return result

    def get_custom_clearance(self):
        """Get custom clearance"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Custom Clearance",
            "view_mode": "tree,form",
            "res_model": "custom.clearance",
            "domain": [("freight_id", "=", self.id)],
            "context": "{'create': False}",
        }

    def track_order(self):
        """Track the order"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Received/Delivered",
            "view_mode": "form",
            "target": "new",
            "res_model": "freight.order.track",
            "context": {"default_freight_id": self.id},
        }

    def create_invoice(self):
        """Create invoice"""
        lines = []
        if self.order_ids:
            for order in self.order_ids:
                value = (
                    0,
                    0,
                    {
                        "name": order.product_id.name,
                        "price_unit": order.price,
                        "quantity": order.volume + order.weight,
                    },
                )
                lines.append(value)

        if self.route_ids:
            for route in self.route_ids:
                value = (
                    0,
                    0,
                    {
                        "name": route.operation_id.name,
                        "price_unit": route.sale,
                    },
                )
                lines.append(value)

        if self.service_ids:
            for service in self.service_ids:
                value = (
                    0,
                    0,
                    {
                        "name": service.service_id.name,
                        "price_unit": service.sale,
                        "quantity": service.qty,
                    },
                )
                lines.append(value)

        invoice_line = {
            "move_type": "out_invoice",
            "partner_id": self.shipper_id.id,
            "invoice_user_id": self.env.user.id,
            "invoice_origin": self.name,
            "ref": self.name,
            "invoice_line_ids": lines,
        }
        inv = self.env["account.move"].create(invoice_line)
        result = {
            "name": "action.name",
            "type": "ir.actions.act_window",
            "views": [[False, "form"]],
            "target": "current",
            "res_id": inv.id,
            "res_model": "account.move",
        }
        self.state = "invoice"
        return result

    def action_cancel(self):
        """Cancel the record"""
        if self.state == "draft":
            self.state = "cancel"
        else:
            raise ValidationError("You can't cancel this order")

        for rec in self:
            rec.state = "cancel"

            mail_content = _("Hi %s,<br>" "The Freight Order %s is Cancelled") % (
                rec.agent_id.name,
                rec.name,
            )
            email_to = self.env["res.partner"].search(
                [
                    (
                        "id",
                        "in",
                        (self.shipper_id.id, self.consignee_id.id, self.agent_id.id),
                    )
                ]
            )
            for mail in email_to:
                main_content = {
                    "subject": _("Freight Order %s is Cancelled") % self.name,
                    "author_id": self.env.user.partner_id.id,
                    "body_html": mail_content,
                    "email_to": mail.email,
                }
                mail_id = self.env["mail.mail"].create(main_content)
                mail_id.mail_message_id.body = mail_content
                mail_id.send()

    def get_invoice(self):
        """View the invoice"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Invoice",
            "view_mode": "tree,form",
            "res_model": "account.move",
            "domain": [("ref", "=", self.name)],
            "context": "{'create': False}",
        }

    @api.depends("name")
    def compute_count(self):
        """Compute custom clearance and account move's count"""
        for freight in self:
            if freight.env["custom.clearance"].search([("freight_id", "=", freight.id)]):
                freight.clearance_count = freight.env["custom.clearance"].search_count(
                    [("freight_id", "=", freight.id)]
                )
            else:
                freight.clearance_count = 0
            if freight.env["account.move"].search([("ref", "=", freight.name)]):
                freight.invoice_count = freight.env["account.move"].search_count(
                    [("ref", "=", freight.name)]
                )
            else:
                freight.invoice_count = 0

    def action_submit(self):
        """Submitting order"""
        for freight in self:
            freight.state = "submit"

            mail_content = _("Hi %s,<br>" "The Freight Order %s is Submitted") % (
                freight.agent_id.name,
                freight.name,
            )
            email_to = self.env["res.partner"].search(
                [
                    (
                        "id",
                        "in",
                        (self.shipper_id.id, self.consignee_id.id, self.agent_id.id),
                    )
                ]
            )
            for mail in email_to:
                main_content = {
                    "subject": _("Freight Order %s is Submitted") % self.name,
                    "author_id": self.env.user.partner_id.id,
                    "body_html": mail_content,
                    "email_to": mail.email,
                }
                mail_id = self.env["mail.mail"].create(main_content)
                mail_id.mail_message_id.body = mail_content
                mail_id.send()

    def action_confirm(self):
        """Confirm order"""
        for freight in self:
            clearance = self.env["custom.clearance"].search(
                [("freight_id", "=", self.id)]
            )
            if clearance:
                if clearance.state == "confirm":
                    freight.state = "confirm"

                    mail_content = _(
                        "Hi %s,<br> " "The Freight Order %s is Confirmed "
                    ) % (freight.agent_id.name, freight.name)
                    email_to = self.env["res.partner"].search(
                        [
                            (
                                "id",
                                "in",
                                (
                                    self.shipper_id.id,
                                    self.consignee_id.id,
                                    self.agent_id.id,
                                ),
                            )
                        ]
                    )
                    for mail in email_to:
                        main_content = {
                            "subject": _("Freight Order %s is Confirmed") % self.name,
                            "author_id": self.env.user.partner_id.id,
                            "body_html": mail_content,
                            "email_to": mail.email,
                        }
                        mail_id = self.env["mail.mail"].create(main_content)
                        mail_id.mail_message_id.body = mail_content
                        mail_id.send()
                elif clearance.state == "draft":
                    raise ValidationError(
                        "the custom clearance ' %s ' is "
                        "not confirmed" % clearance.name
                    )
            else:
                raise ValidationError("Create a custom clearance for %s" % freight.name)

            for line in freight.order_ids:
                line.container_id.state = "reserve"

    def action_done(self):
        """Mark order as done"""
        for freight in self:

            mail_content = _("Hi %s,<br>" "The Freight Order %s is Completed") % (
                freight.agent_id.name,
                freight.name,
            )
            email_to = self.env["res.partner"].search(
                [
                    (
                        "id",
                        "in",
                        (self.shipper_id.id, self.consignee_id.id, self.agent_id.id),
                    )
                ]
            )
            for mail in email_to:
                main_content = {
                    "subject": _("Freight Order %s is completed") % self.name,
                    "author_id": self.env.user.partner_id.id,
                    "body_html": mail_content,
                    "email_to": mail.email,
                }
                mail_id = self.env["mail.mail"].create(main_content)
                mail_id.mail_message_id.body = mail_content
                mail_id.send()
            self.state = "done"

            for line in freight.order_ids:
                line.container_id.state = "available"

    def action_confirm_order(self):
        for freight in self:
            freight.state = "confirm"

    def action_done_order(self):
        for freight in self:
            freight.state = "done"

    def action_cancel_order(self):
        for freight in self:
            freight.state = "cancel"

    def access_error(self):
        for freight in self:
            raise ValidationError(
                "You can not perform this action as you are not admin"
            )
