from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    checklist_ids = fields.One2many("task.checklist", "task_id", string="Checklists")
    checklist_item_ids = fields.One2many(
        "checklist.item",
        compute="_compute_checklist_items",
        string="CheckList Items",
    )

    checklist_progress = fields.Float(
        compute="_compute_checklist_progress",
        store=True,
    )

    @api.depends("checklist_ids.checklist_ids")
    def _compute_checklist_items(self):
        """Get checklist items"""
        for record in self:
            self.checklist_item_ids = [
                (6, 0, record.checklist_ids.mapped("checklist_ids").ids)
            ]

    @api.depends("checklist_ids.checklist_ids.state")
    def _compute_checklist_progress(self):
        """Calculate checklist progress"""
        for record in self:
            total_items = len(record.checklist_item_ids)
            if total_items > 0:
                completed_items = record.checklist_item_ids.filtered(
                    lambda item: item.state == "done"
                )
                progress = (len(completed_items) / total_items) * 100
                record.checklist_progress = progress
            else:
                record.checklist_progress = 0.0
