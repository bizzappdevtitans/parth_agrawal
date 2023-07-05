import logging

from odoo import _

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import IDMissingInBackend

_logger = logging.getLogger(__name__)


class ClickupImporter(AbstractComponent):
    """Base importer for clickup"""

    _name = "clickup.importer"
    _inherit = ["base.importer", "base.clickup.connector"]
    _usage = "record.importer"

    def __init__(self, work_context):
        """Inherit init method."""
        super().__init__(work_context)
        self.external_id = None
        self.clickup_record = None

    def _get_clickup_data(self):
        """Return the raw clickup data for ``self.external_id``"""
        data = self.backend_adapter.read(self.external_id)
        if not data.get(self.backend_adapter._clickup_ext_id_key):
            data[self.backend_adapter._clickup_ext_id_key] = self.external_id
        return data

    def _before_import(self):
        """
        Hook called before the import, when we have the clickup
        data
        """
        return

    def _is_uptodate(self, binding):
        """
        Return True if the import should be skipped because
        it is already up-to-date in OpenERP
        """

    def _import_dependency(
        self, external_id, binding_model, importer=None, always=False
    ):
        """
        Import a dependency.

        The importer class is a class or subclass of
        :class:`ClickupImporter`. A specific class can be defined.

        :param external_id: id of the related binding to import
        :param binding_model: name of the binding model for the relation
        :type binding_model: str | unicode
        :param importer_component: component to use for import
                                   By default: 'importer'
        :type importer_component: Component
        :param always: if True, the record is updated even if it already
                       exists, note that it is still skipped if it has
                       not been modified on clickup since the last
                       update. When False, it will import it only when
                       it does not yet exist.
        :type always: boolean
        """

    def _import_dependencies(self):
        """
         #T-02383 Import the dependencies for the record
        Import of dependencies can be done manually or by calling
        :meth:`_import_dependency` for each dependency.
        """

    def _map_data(self):
        """
        Returns an instance of
        :py:class:`~odoo.addons.connector.components.mapper.MapRecord`

        """
        return self.mapper.map_record(self.clickup_record)

    def _validate_data(self, data):
        """
        Check if the values to import are correct

        Pro-actively check before the ``_create`` or
        ``_update`` if some fields are missing or invalid.

        Raise `InvalidDataError`
        """
        return

    def _must_skip(self):
        """
        Hook called right after we read the data from the backend.

        If the method returns a message giving a reason for the
        skipping, the import will be interrupted and the message
        recorded in the job (if the import is called directly by the
        job, not by dependencies).

        If it returns None, the import will continue normally.

        :returns: None | str | unicode
        """
        return

    def _get_binding(self):
        return self.binder.to_internal(self.external_id)

    def _create_data(self, map_record, **kwargs):
        return map_record.values(for_create=True)

    def _create(self, data):
        """Create the OpenERP record"""
        # special check on data before import

        self._validate_data(data)
        model = self.model.with_context(
            connector_no_export=True, mail_create_nosubscribe=True
        )
        binding = model.sudo().create(data)

        _logger.debug("%d created from clickup %s", binding, self.external_id)
        return binding

    def _update_data(self, map_record, **kwargs):
        return map_record.values(**kwargs)

    def _update(self, binding, data):
        """Update an OpenERP record"""
        # special check on data before import
        self._validate_data(data)
        binding.with_context(connector_no_export=True).write(data)
        _logger.debug("%d updated from clickup %s", binding, self.external_id)
        return

    def _after_import(self, binding, **kwargs):
        """Hook called at the end of the import"""

        return

    def run(self, external_id, force=False, data=None, **kwargs):
        """
        Run the synchronization

        :param external_id: code of the record on clickup
        """
        self.external_id = external_id
        lock_name = "import({}, {}, {}, {})".format(
            self.backend_record._name,
            self.backend_record.id,
            self.work.model_name,
            external_id,
        )

        if data:
            self.clickup_record = data
        else:
            try:
                self.clickup_record = self._get_clickup_data()
            except IDMissingInBackend:
                return _("Record does no longer exist in clickup")

        skip = self._must_skip()  # pylint: disable=assignment-from-none
        if skip:
            return skip

        binding = self._get_binding()
        if not force and self._is_uptodate(binding):
            return _("Already up-to-date.")

        # Keep a lock on this import until the transaction is committed
        # The lock is kept since we have detected that the information
        # will be updated into Odoo
        self.advisory_lock_or_retry(lock_name)
        self._before_import()

        # import the missing linked resources
        self._import_dependencies()

        map_record = self._map_data()

        # project_model = self.env["clickup.project.project"].search(
        #     [("external_id", "=", self.external_id)]
        # )
        if binding:
            record = self._update_data(map_record)
            self._update(binding, record)
        else:
            record = self._create_data(map_record)
            binding = self._create(record)

        self.binder.bind(self.external_id, binding)

        self._after_import(binding, **kwargs)


class BatchImporter(AbstractComponent):
    """
    The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = "clickup.batch.importer"
    _inherit = ["base.importer", "base.clickup.connector"]
    _usage = "batch.importer"

    def _import_record(self, external_id):
        """Import a record directly or delay the import of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError

    # def process_next_batch(self, filters=None, force=False, count=0):
    #     """#T-02072 Method to trigger for next batch import"""
    #     filters["offset"] += filters["limit"]

    #     if filters["offset"] < count:
    #         self.env[self.model._name].with_delay().import_batch(
    #             self.backend_record, filters=filters, force=force
    #         )

    # def get_data_items(self, result, only_ids=False):
    #     """Split the ids and next page information from result of Clickup"""
    #     next_url = result.get("lists", [])
    #     print("next_url", next_url)
    #     items = result.get("_embedded", {}).get("items", [])
    #     if only_ids:
    #         key = self.backend_adapter._akeneo_ext_id_key
    #         items = [item[key] for item in items]
    #     return items, next_url

    # def process_next_page(self, filters=None, job_options=None, **kwargs):
    #     """Method to trigger batch import for Next page"""
    #     if not filters:
    #         filters = {}
    #     job_options = job_options or {}
    #     model = self.env[self.model._name]
    #     if not kwargs.get("no_delay"):
    #         model = model.with_delay(**job_options or {})
    #     model.import_batch(
    #         self.backend_record, filters=filters, job_options=job_options, **kwargs
    #     )


class DirectBatchImporter(AbstractComponent):
    """Import the records directly, without delaying the jobs."""

    _name = "clickup.direct.batch.importer"
    _inherit = "clickup.batch.importer"

    def _import_record(self, external_id):
        """Import the record directly"""

        self.model.import_record(self.backend_record, external_id)


class DelayedBatchImporter(AbstractComponent):
    """Delay import of the records"""

    _name = "clickup.delayed.batch.importer"
    _inherit = "clickup.batch.importer"

    def _import_record(
        self,
        external_id,
        job_options=None,
        data=None,
        model=None,
        force=False,
        **kwargs,
    ):
        """Delay the import of the records"""

        job_options = job_options or {}

        model_parts = model.split(".")
        model_name = " ".join(part.title() for part in model_parts[1:])
        model_name = " ".join(dict.fromkeys(model_name.split()))
        job_options["description"] = f"Import Record of Clickup {model_name}"

        delayable = self.model.with_company(self.backend_record.company_id).with_delay(
            **job_options or {}
        )
        delayable.import_record(
            self.backend_record, external_id, force=force, data=data, **kwargs
        )


class ClickupImportMapperChild(AbstractComponent):
    """:py:class:`MapChild` for the Imports"""

    _name = "clickup.map.child.import"
    _inherit = ["base.clickup.connector", "base.map.child.import"]
