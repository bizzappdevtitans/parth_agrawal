import logging

import psycopg2

from odoo import _, tools
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import RetryableJobError

_logger = logging.getLogger(__name__)


class ClickupExporter(AbstractComponent):
    """A common flow for the exports to Clickup"""

    _name = "clickup.exporter"
    _inherit = ["base.exporter", "base.clickup.connector"]
    _usage = "record.exporter"
    _default_binding_field = "clickup_bind_ids"

    def __init__(self, work_context):
        super().__init__(work_context)
        self.binding = None
        self.external_id = None

    def _has_to_skip(self):
        """Return True if the export can be skipped"""
        return False

    def _map_data(self):
        """Returns an instance of
        :py:class:`~odoo.addons.connector.components.mapper.MapRecord`

        """
        return self.mapper.map_record(self.binding)

    def _lock(self):
        """Lock the binding record.

        Lock the binding record so we are sure that only one export
        job is running for this record if concurrent jobs have to export the
        same record.

        When concurrent jobs try to export the same record, the first one
        will lock and proceed, the others will fail to lock and will be
        retried later.

        This behavior works also when the export becomes multilevel
        with :meth:`_export_dependencies`. Each level will set its own lock
        on the binding record it has to export.

        """
        sql = "SELECT id FROM %s WHERE ID = %%s FOR UPDATE NOWAIT" % self.model._table
        try:
            self.env.cr.execute(sql, (self.binding.id,), log_exceptions=False)
        except psycopg2.OperationalError as err:
            _logger.info(
                "A concurrent job is already exporting the same "
                "record (%s with id %s). Job delayed later.",
                self.model._name,
                self.binding.id,
            )
            raise RetryableJobError from err(
                "A concurrent job is already exporting the same record "
                "(%s with id %s). The job will be retried later."
                % (self.model._name, self.binding.id)
            )

    def _validate_create_data(self, data):
        """Check if the values to import are correct

        Pro-actively check before the ``Model.create`` if some fields
        are missing or invalid

        Raise `InvalidDataError`
        """
        return

    def _validate_update_data(self, data):
        """Check if the values to import are correct

        Pro-actively check before the ``Model.update`` if some fields
        are missing or invalid

        Raise `InvalidDataError`
        """
        return

    def _create_data(self, map_record, fields=None, **kwargs):
        """Get the data to pass to :py:meth:`_create`"""
        return map_record.values(for_create=True, fields=fields, **kwargs)

    def _create(self, data):
        """Create the Clickup record"""
        # special check on data before export
        self._validate_create_data(data)
        return self.backend_adapter.create(data)

    def _update_data(self, map_record, fields=None, **kwargs):
        """Get the data to pass to :py:meth:`_update`"""
        return map_record.values(fields=fields, **kwargs)

    def _update(self, data):
        """Update an Clickup record"""
        assert self.external_id
        # special check on data before export
        self._validate_update_data(data)
        self.backend_adapter.write(self.external_id, data)

    def create_get_binding(self, record, extra_data=None):
        """Search for the existing binding else create new binding"""
        binder = self.binder_for(model=self.model._name)
        external_id = False
        if self._default_binding_field and record[self._default_binding_field]:
            binding = record[self._default_binding_field][:1]
            external_id = binding[self.backend_adapter._odoo_ext_id_key]

        binding = False
        if external_id:
            binding = binder.to_internal(external_id, unwrap=False)
        if not binding:
            binding = self.model.search(
                [
                    ("odoo_id", "=", record.id),
                    ("external_id", "=", False),
                    ("backend_id", "=", self.backend_record.id),
                ],
                limit=1,
            )
        if not binding:
            # create new binding
            data = {}
            if extra_data and isinstance(extra_data, dict):
                data.update(extra_data)
            data.update(
                {
                    "odoo_id": record.id,
                    "external_id": False,
                    "backend_id": self.backend_record.id,
                }
            )
            binding = self.model.create(data)
        return binding

    def run(self, binding, record=None, *args, **kwargs):
        if not binding:
            if not record:
                raise ValidationError(_("No record found to export!!!"))
            binding = self.create_get_binding(record)

        self.binding = binding
        self.external_id = self.binder.to_external(self.binding)
        result = self._run(*args, **kwargs)

        self.binder.bind(self.external_id, self.binding)
        # Commit so we keep the external ID when there are several
        # exports (due to dependencies) and one of them fails.
        # The commit will also release the lock acquired on the binding
        # record
        if not tools.config["test_enable"]:
            self.env.cr.commit()  # pylint: disable=E8102

        self._after_export(self.binding)
        return result

    def _after_export(self, binding):
        pass

    def _export_dependency(
        self,
        relation,
        binding_model,
        component_usage="record.exporter",
        binding_field=None,
        binding_extra_vals=None,
    ):
        exporter = self.component(usage=component_usage, model_name=binding_model)
        if component_usage == "record.importer":
            external_id = relation[exporter.backend_adapter._odoo_ext_id_key]
            return exporter._import_dependency(
                external_id=external_id, binding_model=binding_model
            )

        if binding_field is None:
            binding_field = exporter._default_binding_field

        binding_ids = getattr(relation, binding_field)
        binder = self.binder_for(binding_model)
        if binding_ids.filtered(
            lambda bind: getattr(bind, binder._external_field)
            and bind.backend_id == self.backend_record
        ):
            return

        if not relation:
            return
        # wrap is typically True if the relation is for instance a
        # 'project.project' record but the binding model is
        # 'my_bakend.project.project'
        wrap = relation._name != binding_model

        if wrap and hasattr(relation, binding_field):
            domain = [
                ("odoo_id", "=", relation.id),
                ("backend_id", "=", self.backend_record.id),
            ]
            binding = self.env[binding_model].search(domain)
            if binding:
                assert len(binding) == 1, (
                    "only 1 binding for a backend is " "supported in _export_dependency"
                )
            # we are working with a unwrapped record (e.g.
            # project.project) and the binding does not exist yet.
            # Example: I created a project.task and its binding
            # my_backend.project.task and we are exporting it, but we need
            # to create the binding for the project.project on which it
            # depends.
            else:
                with self._retry_unique_violation():
                    binding = exporter.create_get_binding(
                        record=relation, extra_data=binding_extra_vals
                    )
                    if not tools.config["test_enable"]:
                        self.env.cr.commit()  # pylint: disable=E8102
        else:
            # If my_backend_bind_ids does not exist we are typically in a
            # "direct" binding (the binding record is the same record).
            # If wrap is True, relation is already a binding record.
            binding = relation

        if not binder.to_external(binding):
            exporter.run(binding)

    def _export_dependencies(self):
        """Import the dependencies for the record

        Import of dependencies can be done manually or by calling
        :meth:`_import_dependency` for each dependency.
        """
        if not hasattr(self.backend_adapter, "_model_export_dependencies"):
            return
        record = self.binding.odoo_id
        for dependency in self.backend_adapter._model_export_dependencies:
            model, key = dependency
            relations = record.mapped(key)
            for relation in relations:
                self._export_dependency(
                    relation=relation,
                    binding_model=model,
                )

    def _run(self, fields=None):
        """Flow of the synchronization, implemented in inherited classes"""

        assert self.binding

        if not self.external_id:
            fields = None  # should be created with all the fields

        skip = self._has_to_skip()
        if skip:
            return skip

        # export the missing linked resources
        self._export_dependencies()

        # prevent other jobs to export the same record
        # will be released on commit (or rollback)
        self._lock()

        map_record = self._map_data()

        if self.external_id:
            record = self._update_data(map_record, fields=fields)
            if not record:
                return _("Nothing to export.")
            self._update(record)
        else:
            record = self._create_data(map_record, fields=fields)
            if not record:
                return _("Nothing to export.")
            res = self._create(record)
            if isinstance(res, dict):
                self.external_id = res.get(self.backend_adapter._clickup_ext_id_key)
            else:
                self.external_id = self.binding[self.backend_adapter._odoo_ext_id_key]

        return _("Record exported with ID %s on Backend.") % self.external_id


class BatchExporter(AbstractComponent):
    """The role of a BatchExporter is to search for a list of
    items to export, then it can either export them directly or delay
    the export of each item separately.
    """

    _name = "clickup.batch.exporter"
    _inherit = ["base.exporter", "base.clickup.connector"]
    _usage = "batch.exporter"

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

    def _export_record(self, record, job_options=None, **kwargs):
        """Delay the export of the records"""

        job_options = job_options or {}

        model_name = self.queue_job_description()
        job_options["description"] = f"Export Record of Clickup {model_name}"

        delayable = self.model.with_delay(**job_options or {})
        delayable.export_record(self.backend_record, record, **kwargs)
