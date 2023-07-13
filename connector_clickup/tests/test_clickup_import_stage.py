import logging

from .common import ClickupTestCase, recorder

_logger = logging.getLogger(__name__)


class TestImportStage(ClickupTestCase):
    def setUp(self):
        super().setUp()

    @recorder.use_cassette
    def test_00_import_stage(self):
        """Import of a task"""
        external_id = "90020424787"
        self.binding = self._import_record(
            filename="import_00_project_task_type",
            model_name="clickup.project.task.type",
            external_id=external_id,
            backend=self.backend,
        )
        stage_model = self.env["clickup.project.task.type"]
        stage = stage_model.search([("external_id", "=", external_id)])
        self.assertEqual(len(stage), 1)

        self.assertEqual(stage.odoo_id.name, "filler")  # Name
