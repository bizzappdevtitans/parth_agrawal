import urllib
from contextlib import contextmanager
from os.path import dirname, join

import mock
from vcr import VCR

import odoo
from odoo.tools import mute_logger

from odoo.addons.component.tests.common import SavepointComponentCase

recorder = VCR(
    cassette_library_dir=join(dirname(__file__), "fixtures/cassettes"),
    decode_compressed_response=True,
    filter_headers=["Authorization"],
    path_transformer=VCR.ensure_suffix(".yaml"),
    record_mode="once",
)


class MockResponseImage(object):
    def __init__(self, resp_data, code=200, msg="OK"):
        self.resp_data = resp_data
        self.content = resp_data
        self.status_code = code
        self.msg = msg
        self.headers = {"Content-Type": "application/json"}

    def raise_for_status(self):
        if self.status_code != 200:
            raise urllib.error.HTTPError(
                "", self.status_code, str(self.status_code), None, None
            )

    def read(self):
        # pylint: disable=method-required-super
        return self.resp_data

    def getcode(self):
        return self.code


class ClickupTestCase(SavepointComponentCase):
    def setUp(self):
        """#T-02182 configurations for backend."""
        super(ClickupTestCase, self).setUp()
        self.recorder = recorder
        # T-02182 disable commits when run from pytest/nosetest

        # self.url1 = "https://api.clickup.com/api/v2/"
        self.backend_record = self.env["clickup.backend"]
        self.backend = self.backend_record.create(
            {
                "name": "Test Clickup",
                "uri": "90020435594",
                "api_key": "pk_67222607_9TATNL43QDZ5M0KWHNLQPF41L3EFNQLM",
            }
        )

    def _import_record(self, model_name, external_id, cassette=True):
        assert model_name.startswith("clickup.")
        table_name = model_name.replace(".", "_")

        # strip 'shopify_' from the model_name to shorted the filename
        filename = "import_%s" % (table_name[8:])

        def run_import():
            with mute_logger(
                "odoo.addons.mail.models.mail_mail", "odoo.models.unlink", "odoo.tests"
            ):
                # with mock_urlopen_image():
                self.env[model_name].import_record(self.backend, external_id)

        if cassette:
            with self.recorder.use_cassette(filename):
                run_import()
        else:
            run_import()

        binding = self.env[model_name].search(
            [("backend_id", "=", self.backend.id), ("external_id", "=", external_id)]
        )
        self.assertEqual(len(binding), 1)
        return binding
