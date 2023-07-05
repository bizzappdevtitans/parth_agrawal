import logging
from datetime import date, datetime, timedelta

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.addons.connector.exception import MappingError
from odoo.addons.queue_job.exception import NothingToDoJob

_logger = logging.getLogger(__name__)


class ProjectTaskImporter(Component):
    _name = "clickup.project.task.importer"
    _inherit = "clickup.importer"
    _apply_on = "clickup.project.tasks"

    def _is_uptodate(self, binding):
        """
        Return True if the import should be skipped because
        it is already up-to-date in OpenERP
        """
        # if the last synchronization date is greater than the last
        # update in clickup, we skip the import.
        # Important: at the beginning of the exporters flows, we have to
        # check if the clickup_date is more recent than the sync_date
        # and if so, schedule a new import. If we don't do that, we'll
        # miss changes done in clickup
        super()._is_uptodate(binding)
        assert self.clickup_record
        last_update_date = self.backend_adapter._last_update_date
        update_date = self.clickup_record.get(last_update_date, "")
        timestamp = int(update_date) / 1000
        if (
            not update_date
            or not binding
            or (binding and not hasattr(binding, "updated_at"))
        ):
            return  # no update date on clickup, always import it.
        sync_date = binding.updated_at
        if not sync_date:
            return
        clickup_date = datetime.fromtimestamp(timestamp)
        return clickup_date <= sync_date

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

        if not external_id:
            return
        project_model = self.env["clickup.project.project"].search(
            [("external_id", "=", external_id)]
        )
        if project_model:
            return
        binder = self.binder_for(binding_model)
        if not binder.to_internal(external_id):
            if importer is None:
                importer = self.component(
                    usage="record.importer", model_name=binding_model
                )
            try:
                importer.run(external_id)
            except NothingToDoJob:
                _logger.info(
                    "Dependency import of %s(%s) has been ignored.",
                    binding_model._name,
                    external_id,
                )

    def _import_dependencies(self):
        """
         #T-02383 Import the dependencies for the record
        Import of dependencies can be done manually or by calling
        :meth:`_import_dependency` for each dependency.
        """
        if not hasattr(self.backend_adapter, "_model_dependencies"):
            return

        for dependency in self.backend_adapter._model_dependencies:
            model, key = dependency
            external_id = self.clickup_record.get(key).get("id")

            self._import_dependency(
                external_id=external_id, binding_model="clickup.project.project"
            )


class ProjectTaskBatchImporter(Component):
    """Delay import of the records"""

    _name = "clickup.project.task.batch.importer"
    _inherit = "clickup.delayed.batch.importer"
    _apply_on = "clickup.project.tasks"

    def run(self, filters=None, force=False):
        """Run the synchronization"""
        from_date = filters.pop("from_date", None)
        to_date = filters.pop("to_date", None)
        records = self.backend_adapter.search(
            filters, from_date=from_date, to_date=to_date
        )

        for record in records:
            tasks = record.get("tasks", [])
            for task in tasks:
                external_id = task.get(self.backend_adapter._clickup_ext_id_key)

                self._import_record(
                    external_id, data=task, force=force, model=self._apply_on
                )


class ProjectTaskImportMapper(Component):
    _name = "clickup.project.task.import.mapper"
    _inherit = "clickup.import.mapper"
    _apply_on = "clickup.project.tasks"

    # children = [
    #     (
    #         "tags",
    #         "tag_ids",
    #         "clickup.project.tasks",
    #     ),
    # ]

    @only_create
    @mapping
    def odoo_id(self, record):
        """Getting product based on the SKU."""

        binder = self.binder_for(model="clickup.project.tasks")
        task = binder.to_internal(record.get("id"), unwrap=True)

        if not task:
            return {}
        return {"odoo_id": task.id}

    @mapping
    def project_id(self, record):
        project = record.get("list").get("id")
        company_id = self.backend_record.company_id
        project_id = self.env["project.project"].search(
            [
                ("external_id", "=", project),
                ("company_id", "=", company_id.id),
            ],
        )

        if not project_id:
            raise MappingError(_("Project not found for ID: %s") % project_id)

        return {"project_id": project_id.id}

    # binder = self.binder_for(model="clickup.project.project")

    # project = binder.to_internal(project_id, unwrap=True)
    # if not project:
    #     raise MappingError(_("Project not found for ID: %s") % project_id)

    # return {"odoo_id": project.id}

    @mapping
    def stage_id(self, record):
        stage_id = record.get("status").get("status")

        stage = self.env["project.task.type"].search([("name", "=", stage_id)], limit=1)

        return {"stage_id": stage.id}

    @mapping
    def name(self, record):
        name = record.get("name")
        return {
            "name": name,
        }

    @mapping
    def description(self, record):
        description = record.get("text_content")

        return {"description": description}

    @mapping
    def external_id(self, record):
        """#T-02383 Mapped external id"""

        external_id = record.get("id")

        return {"external_id": external_id}

    @mapping
    def backend_id(self, record):
        """Mapped the backend id"""
        backend_id = self.backend_record.id

        return {"backend_id": backend_id}

    @mapping
    def project_info(self, record):
        """Mapped the backend id"""
        project_id = record.get("list").get("id")

        return {"project_info": project_id}

    @mapping
    def date_deadline(self, record):
        """Mapped the backend id"""
        due_data = record.get("due_date")

        if due_data:
            timestamp = int(due_data) / 1000
            due_date = date.fromtimestamp(timestamp) + timedelta(days=1)
            return {"date_deadline": due_date}

    @mapping
    def created_at(self, record):
        """Mapped the backend id"""
        created_at = record.get("date_created")
        if created_at:
            timestamp = int(created_at) / 1000
            date_created = datetime.fromtimestamp(timestamp)
            return {"created_at": date_created}
        else:
            return {}

    @mapping
    def updated_at(self, record):
        """Mapped the backend id"""

        updated_at = record.get("date_updated")
        if updated_at:
            timestamp = int(updated_at) / 1000
            date_updated = datetime.fromtimestamp(timestamp)
            return {"updated_at": date_updated}
        else:
            return {}


# class ClickupProjectTaskTagsImportMapper(Component):
#     _name = "clickup.project.task.import.child.mapper"
#     _inherit = "clickup.map.child.import"
#     _apply_on = "clickup.project.tasks"

#     @mapping
#     def tag_ids(self, record):
#         print("\n\ninside tag ids\n\n")
#         tags = record.get("tags")

#         tag_model = self.env["project.tags"]
#         tag_ids = []
#         for tag in tags:
#             tag_name = tag.get("name")
#             domain = [("name", "=", tag_name)]
#             existing_tag = tag_model.search(domain, limit=1)
#             if existing_tag:
#                 tag_ids.append(existing_tag.id)
#             else:
#                 new_tag = tag_model.create({"name": tag_name})
#                 tag_ids.append(new_tag.id)

#         return {"tag_ids": [(6, 0, tag_ids)]}
