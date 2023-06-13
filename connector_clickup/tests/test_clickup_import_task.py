from .common import ClickupTestCase, recorder


class TestImportTask(ClickupTestCase):
    @classmethod
    def setUpClass(cls):
        """Setup test class for connector shopify to remove queue job."""
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,  # no jobs thanks
            )
        )

    def setUp(self):
        """Setup configuration for Partner."""
        super(TestImportTask, self).setUp()

    @recorder.use_cassette
    def test_00_import_task(self):
        """Import of a tasks"""
        external_id = "85zt6b21b"
        self.binding = self._import_record(
            "clickup.project.tasks", external_id=external_id
        )
        task_model = self.env["clickup.project.tasks"]
        task = task_model.search([("external_id", "=", external_id)])

        self.assertEqual(len(task), 1)
        self.assertEqual(task.external_id, "85zt6b21b")  # task id
        self.assertEqual(
            task.odoo_id.project_id.external_id, "900200890774"
        )  # project_id
        self.assertEqual(task.odoo_id.name, "again inside again")  # Name
        # self.assertEqual(task.odoo_id.description, "")  # Description
