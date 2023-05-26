"""
Exporters for Everstox.

In addition to its export job, an exporter has to:

* check in Everstox if the record has been updated more recently than the
  last sync date and if yes, delay an import
* call the ``bind`` method of the binder to update the last sync date

"""
import logging

from odoo.addons.component.core import AbstractComponent
from odoo.addons.queue_job.job import identity_exact

_logger = logging.getLogger(__name__)


class ClickupExporter(AbstractComponent):
    """A common flow for the exports to Everstox"""

    _name = "clickup.exporter"
    _inherit = ["base.exporter", "base.clickup.connector"]
    _usage = "record.exporter"
    # _default_binding_field = "everstox_bind_ids"


class BatchExporter(AbstractComponent):
    """The role of a BatchExporter is to search for a list of
    items to export, then it can either export them directly or delay
    the export of each item separately.
    """

    _name = "clickup.batch.exporter"
    _inherit = ["base.exporter", "base.clickup.connector"]
    _usage = "batch.exporter"

    # def run(self, filters=None):
    #     """Run the synchronization"""
    #     records = self.backend_adapter.search(filters)
    #     print("Export RECORD TYPE", records)
    #     for record in records:
    #         self._export_record(record)

    def run(self, filters=None):
        """Run the synchronization"""
        records = self.backend_adapter.search(filters)

        self._export_record(records)

    def _export_record(self, external_id):
        """Export a record directly or delay the export of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError


class DirectBatchExporter(AbstractComponent):
    """Export the records directly, without delaying the jobs."""

    _name = "clickup.direct.batch.exporter"
    _inherit = "clickup.batch.exporter"


class DelayedBatchExporter(AbstractComponent):
    """Delay export of the records"""

    _name = "clickup.delayed.batch.exporter"
    _inherit = "clickup.batch.exporter"

    def _export_record(self, records, job_options=None, **kwargs):
        """Delay the export of the records"""

        job_options = job_options or {}
        if "identity_key" not in job_options:
            job_options["identity_key"] = identity_exact
        delayable = self.model.with_delay(**job_options or {})
        delayable.export_record(self.backend_record, records, **kwargs)
