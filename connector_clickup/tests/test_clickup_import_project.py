from .common import ClickupTestCase, recorder


class TestImportProject(ClickupTestCase):
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
        super(TestImportProject, self).setUp()

    @recorder.use_cassette
    def test_00_import_project(self):
        """Import of a partner"""
        external_id = "900200890774"
        self.binding = self._import_record(
            "clickup.project.project", external_id=external_id
        )
        project_model = self.env["clickup.project.project"]
        project = project_model.search([("external_id", "=", external_id)])

        self.assertEqual(len(project), 1)
        self.assertEqual(project.external_id, "900200890774")  # project id
        self.assertEqual(project.odoo_id.name, "AGAIN")  # Name
        self.assertEqual(project.odoo_id.description, "")  # Description

        # self.assertEqual(
        #     project.admin_graphql_api_id, "gid:\\/\\/shopify\\/Customer\\/4653534707909"
        # )  # admin_graphql_api_id
