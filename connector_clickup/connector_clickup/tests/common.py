from os.path import dirname, join

from vcr import VCR

from odoo.addons.component.tests.common import TransactionComponentCase

recorder = VCR(
    cassette_library_dir=join(dirname(__file__), "fixtures/cassettes"),
    decode_compressed_response=True,
    filter_headers=["Authorization"],
    path_transformer=VCR.ensure_suffix(".yaml"),
)


class ClickupTestCase(TransactionComponentCase):
    recorder = VCR(
        cassette_library_dir=join(dirname(__file__), "fixtures/cassettes"),
        decode_compressed_response=True,
        filter_headers=["Authorization"],
        path_transformer=VCR.ensure_suffix(".yaml"),
    )

    def setUp(self):
        """#T-02452 configurations for backend."""
        super().setUp()
        company_model = self.env["res.company"]
        company = company_model.create({"name": "Your Company Name"})
        self.recorder.allow_playback_repeats = True
        self.url_test = "https://api.clickup.com"
        self.backend_record = self.env["clickup.backend"]
        self.backend = self.backend_record.create(
            {
                "test_location": self.url_test,
                "name": "Test Connector Clickup",
                "test_token": """67222607_393707bcb12bcf9ea0ec8d7f3
                947852b97d1cae9df5f2d30869972b8d11a5d6c""",
                "test_mode": True,
                "company_id": company.id,
            }
        )

    def _import_record(
        self, model_name, external_id=None, data=None, filename=None, backend=None
    ):
        """
        # T-06257 Generic method, may change the fields parameter if different
        scenarios occurred.
        """
        assert model_name.startswith("clickup.")
        if not backend:
            backend = self.env["clickup.backend"].search([], limit=1)
        with recorder.use_cassette(filename):
            self.env[model_name].import_record(
                backend=backend, external_id=external_id, data=data
            )
