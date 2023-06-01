import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

_logger = logging.getLogger(__name__)


class ProjectTaskTypeImporter(Component):
    _name = "clickup.project.task.type.importer"
    _inherit = "clickup.importer"
    _apply_on = "clickup.project.task.type"

    def __init__(self, work_context):
        """Inherit init method."""
        work_context.model = work_context.model.with_context(
            create_product_product=False
        )
        super(ProjectTaskTypeImporter, self).__init__(work_context)

    def _after_import(self, binding, **kwargs):
        """Hook called at the end of the import"""
        # images
        # T-02210 Iterate over all akeneo_image_ids read file and set image URL
        # for akeneo_image in binding.akeneo_image_ids:
        #     if not akeneo_image.image_path:
        #         continue
        #     image_path = akeneo_image.image_path
        #     image_value = self.get_image_url(image_path)
        #     image_url = image_value.get("value", {}).get("value")
        #     akeneo_image.write({"image_url": image_url})
        return super(ProjectTaskTypeImporter, self)._after_import(binding, **kwargs)


class ProjectTaskTypeBatchImporter(Component):
    """Delay import of the records"""

    _name = "clickup.project.task.type.batch.importer"
    _inherit = "clickup.delayed.batch.importer"
    _apply_on = "clickup.project.task.type"

    # def run(self, filters=None, force=False):
    #     """Run the synchronization"""

    #     records = self.backend_adapter.search(filters)
    #     print("\n\n inside run records==", records)
    #     for record in records:
    #         print("\n\n loop record", record)
    #         if record != []:
    #             continue

    #         tasks = record.get("tasks", [])
    #         for task in tasks:
    #             external_id = task.get(self.backend_adapter._akeneo_ext_id_key)

    #             self._import_record(external_id, data=task, force=force)

    def run(self, filters=None, force=False):
        """Run the synchronization"""

        records = self.backend_adapter.search(filters)

        for record in records:
            tasks = record.get("tasks", [])
            for task in tasks:
                external_id = task.get(self.backend_adapter._akeneo_ext_id_key)

                self._import_record(external_id, data=task, force=force)


class ProjectTaskTypeImportMapper(Component):
    _name = "clickup.project.task.type.import.mapper"
    _inherit = "clickup.import.mapper"
    _apply_on = "clickup.project.task.type"

    @only_create
    @mapping
    def odoo_id(self, record):
        """Getting product based on the SKU."""
        binder = self.binder_for(model="clickup.project.task.type")
        odoo_id = binder.to_internal(record.get("status").get("status"), unwrap=True)
        if not odoo_id:
            return {}
        return {"odoo_id": odoo_id.id}

    @mapping
    def name(self, record):
        status_name = record.get("status").get("status")
        return {"name": status_name}

    @mapping
    def external_id(self, record):
        """#T-02383 Mapped external id"""
        external_id = record.get("status")

        return {"external_id": external_id}

    @mapping
    def backend_id(self, record):
        """Mapped the backend id"""
        data = self.backend_record.id

        return {"backend_id": data}
