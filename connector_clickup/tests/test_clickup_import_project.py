from .common import ClickupTestCase, recorder


class TestImportProject(ClickupTestCase):
    @classmethod
    def setUpClass(cls):
        """Setup test class for connector trello to remove queue job."""
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,  # no jobs
            )
        )

    def setUp(self):
        """Setup configuration for Project."""
        super().setUp()

    @recorder.use_cassette
    def test_00_import_project(self):
        """Import of a project"""
        external_id = "900200890774"
        self.binding = self._import_record(
            filename="import_00_project_project",
            model_name="clickup.project.project",
            external_id=external_id,
            backend=self.backend,
        )
        project_model = self.env["clickup.project.project"]

        project = project_model.search([("external_id", "=", external_id)])
        # Create a new company record

        self.assertEqual(len(project), 1)
        self.assertEqual(project.company_id.name, "Your Company Name")
        self.assertEqual(project.external_id, "900200890774")  # project id
        self.assertEqual(project.odoo_id.name, "AGAIN")  # Name
        self.assertEqual(
            project.odoo_id.description, "<p>{{([])([])}}</p>"
        )  # Description
