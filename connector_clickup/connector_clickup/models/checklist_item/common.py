from odoo import api, fields, models

from odoo.addons.component.core import Component


class ClickupChecklistItem(models.Model):
    _name = "clickup.checklist.item"
    _inherit = ["clickup.binding"]
    _inherits = {"checklist.item": "odoo_id"}
    _description = "Clickup Checklist Item binding model"

    odoo_id = fields.Many2one("checklist.item", required=True, ondelete="restrict")
    clickup_checklist_item_id = fields.Many2one("clickup.task.checklist")

    @api.model
    def create(self, vals):
        """to set the checklist_id of checklist.
        while importing checklist for the first time
        - added here as in mapping no binding exists
         to identify based on external id"""
        if not vals.get("checklist_id"):
            clickup_checklist_item_id = vals.get("clickup_checklist_item_id")
            if not clickup_checklist_item_id:
                return super().create(vals)
            binding = self.env["clickup.task.checklist"].browse(
                clickup_checklist_item_id
            )
            vals["checklist_id"] = binding.odoo_id.id
        return super().create(vals)


class ChecklistItem(models.Model):
    _inherit = "checklist.item"

    clickup_bind_ids = fields.One2many(
        "clickup.checklist.item",
        "odoo_id",
        readonly=True,
    )

    clickup_backend_id = fields.Many2one(
        "clickup.backend",
        related="clickup_bind_ids.backend_id",
        string="Clickup Backend",
        readonly=True,
        store=True,
    )


class ChecklistItemAdapter(Component):
    _name = "clickup.checklist.item.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.checklist.item"
    _clickup_model = "/checklist/{}/checklist_item"
    _clickup_ext_id_key = "id"

    def write(self, external_id, data):
        """Update records on the external system"""
        resource_path = "/checklist/{}/checklist_item".format(
            data.get("task_checklist_id")
        )
        self._clickup_model = resource_path
        return super().write(external_id, data)
