from odoo import api, fields, models


class ClickupAbstractModel(models.AbstractModel):
    _name = "clickup.model"
    _inherit = "external.binding"
    _description = "Clickup abstract model"

    backend_id = fields.Many2one("clickup.backend", string="Clickup Backend")
    external_id = fields.Char(string="External ID")
    api_token_data = fields.Char(string="API token")

    @api.model
    def import_batch(
        self, backend, filters=None, force=False, job_options=None, **kwargs
    ):
        """Prepare the import of records from ClickUp"""
        if filters is None:
            filters = {}
        with backend.work_on(self._name) as work:
            importer = work.component(usage="batch.importer")
            return importer.run(filters=filters, force=force)

    @api.model
    def import_record(self, backend, external_id, force=False, data=None, **kwargs):
        """Import a ClickUp Project record"""

        with backend.work_on(self._name) as work:
            importer = work.component(usage="record.importer")

            return importer.run(external_id, force=force, data=data, **kwargs)

    @api.model
    def export_batch(self, backend, filters=None):
        """Prepare the export of records modified on in odoo"""

        if filters is None:
            filters = {}
        with backend.work_on(self._name) as work:
            exporter = work.component(usage="batch.exporter")
            return exporter.run(filters=filters)

    # @api.model
    # def export_record(self, backend, record, fields=None):
    #     """Export a record on Clickup"""
    #     print("\n\nexport_records=", record)
    #     # for record in record:
    #     #     print("\n\nLOOP of export_record", record)
    #     with backend.work_on(self._name) as work:
    #         exporter = work.component(usage="record.exporter")
    #         return exporter.run(self, record, fields)

    def export_record(self, backend, record, fields=None):
        """Export a record on scayle"""
        record.ensure_one()
        with backend.work_on(self._name) as work:
            exporter = work.component(usage="record.exporter")
            return exporter.run(self, record, fields)
