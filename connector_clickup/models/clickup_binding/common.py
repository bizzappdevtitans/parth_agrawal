from odoo import api, fields, models


class ClickupBinding(models.AbstractModel):
    _name = "clickup.binding"
    _inherit = "external.binding"
    _description = "Clickup Binding Model"

    backend_id = fields.Many2one("clickup.backend")
    external_id = fields.Char()

    @api.model
    def import_batch(
        self, backend, filters=None, force=False, job_options=None, **kwargs
    ):
        if filters is None:
            filters = {}

        with backend.work_on(self._name) as work:
            importer = work.component(usage="batch.importer")
            return importer.run(filters=filters, force=force, job_options=job_options)

    @api.model
    def import_record(self, backend, external_id, force=False, data=None, **kwargs):
        with backend.work_on(self._name) as work:
            importer = work.component(usage="record.importer")

            return importer.run(external_id, force=force, data=data, **kwargs)

    @api.model
    def export_batch(self, backend, job_options=None, filters=None):
        if filters is None:
            filters = {}
        with backend.work_on(self._name) as work:
            exporter = work.component(usage="batch.exporter")
            return exporter.run(filters=filters, job_options=job_options)

    def export_record(self, backend, record, fields=None):
        record.ensure_one()
        with backend.work_on(self._name) as work:
            exporter = work.component(usage="record.exporter")
            return exporter.run(self, record, fields)
