import logging

from .common import ClickupTestCase, recorder

_logger = logging.getLogger(__name__)


class TestImportTask(ClickupTestCase):
    def setUp(self):
        """Setup configuration for Project."""
        super().setUp()

    @recorder.use_cassette
    def test_00_import_tasks(self):
        """Import of a project"""
        external_id = "85zt6b21b"
        self.binding = self._import_record(
            filename="import_00_project_tasks",
            model_name="clickup.project.task",
            external_id=external_id,
            backend=self.backend,
        )
        task_model = self.env["clickup.project.task"]
        task = task_model.search([("external_id", "=", external_id)])
        self.assertEqual(len(task), 1)
        self.assertEqual(task.external_id, "85zt6b21b")  # task id

        self.assertEqual(task.odoo_id.name, "again inside again")  # Name
        # self.assertEqual(task.odoo_id.description, "")  # Description
