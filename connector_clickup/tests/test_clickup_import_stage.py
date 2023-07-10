import logging

from .common import ClickupTestCase, recorder

_logger = logging.getLogger(__name__)


class TestImportStage(ClickupTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,  # no jobs
            )
        )

    def setUp(self):
        super().setUp()

    @recorder.use_cassette
    def test_00_import_tasks(self):
        """Import of a project"""
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
        # self.assertEqual(stage.external_id, "p90020155368_40s86Lwa")  # task id

        self.assertEqual(stage.odoo_id.name, "filler")  # Name
        # self.assertEqual(task.odoo_id.description, "")  # Description
