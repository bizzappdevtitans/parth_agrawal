import logging
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from urllib.parse import urlencode

from odoo import fields, http, models

from odoo.addons.component.core import Component

# from ...components.backend_adapter import ClickUpBackendAdapter
from ...components.backend_adapter import (
    ClickupAPI,
    ClickupLocation,
    ClickupTokenLocation,
)
from ...components.misc import to_iso_datetime

# Create a thread-local storage to hold the authorization code
thread_local = threading.local()
# Create a server-side storage to store the callback URL
callback_storage = {}

_logger = logging.getLogger(__name__)

IMPORT_DELTA_BUFFER = 30  # seconds

EXPORT_DELTA_BUFFER = 30  # seconds


class ClickupBackend(models.Model):
    _name = "clickup.backend"
    _inherit = "connector.backend"
    _description = "Clickup backend"

    name = fields.Char()
    auth_type = fields.Selection(
        [("api_key", "API Key"), ("Oauth", "Oauth Authentication")],
        required=True,
        default="api_key",
        help="Select Authentication Type",
    )

    datetime_filter_task = fields.Datetime(
        help="""This will get all the tasks which is created
         or updated after your provided date and time"""
    )
    limit = fields.Integer(default=100)

    force_update_tasks = fields.Boolean()
    company_id = fields.Many2one(comodel_name="res.company", string="Company")

    # Live
    api_key = fields.Char(help="Enter API Key")
    uri = fields.Char(help="Enter End Point Location Of Space Id")
    client_id = fields.Char()
    client_secret = fields.Char()
    username = fields.Char()
    password = fields.Char()

    # Test
    test_mode = fields.Boolean(default=True)
    test_token = fields.Char()
    test_location = fields.Char()

    # def _compute_company_id(self):
    #     for record in self:
    #         record.company_id = self.env.company.id

    def toggle_test_mode(self):
        for record in self:
            record.test_mode = not record.test_mode

    def _import_from_date(
        self,
        model,
        from_date_field=None,
        filters=None,
        force_update_field=None,
        priority=None,
        with_delay=True,
    ):
        """Common method for import data from from_date."""
        if not filters:
            filters = {}
        import_start_time = datetime.now()
        import_start_time_new = int(import_start_time.timestamp() * 1000)
        job_options = {}
        if priority or priority == 0:
            job_options["priority"] = priority
        for backend in self:
            if from_date_field:
                from_date = backend[from_date_field]
                if from_date:
                    from_date = int(from_date.timestamp() * 1000)

                    filters = {"from_date": from_date, "to_date": import_start_time_new}

            filters["limit"] = backend.limit
            filters["with_count"] = "true"
            force = False
            if force_update_field:
                force = backend[force_update_field]

            model_parts = model.split(".")
            model_name = " ".join(part.title() for part in model_parts[1:])
            model_name = " ".join(dict.fromkeys(model_name.split()))
            job_options["description"] = f"Import Batch of Clickup {model_name}"

            self.env[model].with_company(backend.company_id).with_delay(
                **job_options or {}
            ).import_batch(
                backend,
                filters=filters,
                force=force,
                job_options=job_options,
            )

            if force:
                backend[force_update_field] = False
        next_time = import_start_time - timedelta(seconds=IMPORT_DELTA_BUFFER)
        if from_date_field:
            self.write({from_date_field: next_time})

    def import_projects(self, with_delay=True):
        """#T-02421 Import Clickup References"""

        for backend in self:
            backend._import_from_date(
                model="clickup.project.project",
                from_date_field=None,
                priority=5,
                with_delay=with_delay,
                force_update_field=None,
            )

    def import_tasks(self, with_delay=True):
        for backend in self:
            backend._import_from_date(
                model="clickup.project.tasks",
                from_date_field="datetime_filter_task",
                priority=10,
                with_delay=with_delay,
                force_update_field="force_update_tasks",
            )

    def import_stages(self, with_delay=True):
        for backend in self:
            backend._import_from_date(
                model="clickup.project.task.type",
                from_date_field=None,
                priority=7,
                with_delay=with_delay,
                force_update_field=None,
            )

    @contextmanager
    def work_on(self, model_name, **kwargs):
        """Add the work on for clickup."""
        self.ensure_one()
        location = self.uri
        client_id = self.client_id
        client_secret = self.client_secret
        token = self.api_key
        username = self.username
        password = self.password
        if self.test_mode:
            location = kwargs.get("location", self.location)
            client_id = self.client_id
            client_secret = self.client_secret
            token = self.token
            username = self.username
            password = self.password

        clickup_location = ClickupLocation(
            location=location,
            token=token,
        )

        # Clickup have different endpoint/credentials for token
        clickup_location_token = ClickupTokenLocation(
            location=location,
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
        )
        with ClickupAPI(clickup_location, clickup_location_token) as clickup_api:
            _super = super()
            # from the components we'll be able to do: self.work.clickup_api
            with _super.work_on(model_name, clickup_api=clickup_api, **kwargs) as work:
                yield work

    def export_projects(self, with_delay=True, from_sync=False):
        for backend in self.sudo():
            backend._export_from_date(
                model="clickup.project.project",
                from_date_field=None if not from_sync else False,
                with_delay=with_delay,
            )

    def export_tasks(self, with_delay=True, from_sync=False):
        for backend in self.sudo():
            backend._export_from_date(
                model="clickup.project.tasks",
                from_date_field=None if not from_sync else False,
                with_delay=with_delay,
            )

    def _export_from_date(
        self,
        model,
        from_date_field=None,
        filters=None,
        force_update_field=None,
        priority=None,
        with_delay=True,
    ):
        """Common method for import data from from_date."""

        if not filters:
            filters = {}
        import_start_time = datetime.now()
        job_options = {}
        if priority or priority == 0:
            job_options["priority"] = priority
        for backend in self:
            from_date = None
            if from_date_field:
                from_date = backend[from_date_field]
                if from_date:
                    from_date = from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                else:
                    from_date = to_iso_datetime(from_date)

            filters["limit"] = backend.limit
            filters["with_count"] = "true"
            force = False
            if force_update_field:
                force = backend[force_update_field]

            model_parts = model.split(".")
            model_name = " ".join(part.title() for part in model_parts[1:])
            model_name = " ".join(dict.fromkeys(model_name.split()))
            job_options["description"] = f"Export Batch of Clickup {model_name}"

            clickup_model = (
                self.env[model].with_delay(**job_options or {})
                if with_delay
                else self.env[model]
            )

            clickup_model.export_batch(
                backend,
                filters=filters,
            )
            if force:
                backend[force_update_field] = False
        next_time = import_start_time - timedelta(seconds=IMPORT_DELTA_BUFFER)
        if from_date_field:
            self.write({from_date_field: next_time})

    def cron_import_clickup_changes(
        self,
        filters=None,
        with_delay=True,
    ):
        data = self.env["clickup.backend"].search([])

        for backend in data:
            clickup_model = backend.env["clickup.project.project"].with_delay()
            clickup_model.import_batch(
                backend,
                filters=filters,
                force=True,
                **{"no_delay": not with_delay},
            )
        for backend in data:
            clickup_model = backend.env["clickup.project.task.type"].with_delay()
            clickup_model.import_batch(
                backend,
                filters=filters,
                force=True,
                **{"no_delay": not with_delay},
            )
        for backend in data:
            clickup_model = backend.env["clickup.project.tasks"].with_delay()
            clickup_model.import_batch(
                backend,
                filters=filters,
                force=True,
                **{"no_delay": not with_delay},
            )

    def cron_export_clickup_changes(
        self,
        filters=None,
        with_delay=True,
    ):
        data = self.env["clickup.backend"].search([])

        for backend in data:
            clickup_model = backend.env["clickup.project.project"].with_delay()
            clickup_model.export_batch(
                backend,
                filters=filters,
            )
        for backend in data:
            clickup_model = backend.env["clickup.project.tasks"].with_delay()
            clickup_model.export_batch(
                backend,
                filters=filters,
            )

    # def generate_token(self):
    #     """Generate token for clickup."""
    #     with self.work_on(self._name) as work:
    #         backend_adapter = work.component(usage="backend.adapter")
    #         token_dict = backend_adapter.get_token()
    #         token = token_dict.get("access_token")
    #         if self.test_mode:
    #             self.test_token = token
    #         else:
    #             self.api_key = token

    # def get_authorization_url(self):
    #     params = {
    #         "client_id": self.client_id,
    #         "redirect_uri": self.redirect_uri,
    #         "response_type": "code",
    #         "scope": "read",
    #     }
    #     authorization_url = "https://oauth-provider.com/authorize?" + urlencode(params)
    #     return authorization_url

    # @api.route("/oauth/callback")
    # def handle_callback(self, **kwargs):
    #     authorization_code = kwargs.get("code")
    #     self.exchange_authorization_code(authorization_code)

    # def exchange_authorization_code(self, authorization_code):
    #     token_endpoint = "https://oauth-provider.com/token"
    #     data = {
    #         "grant_type": "authorization_code",
    #         "client_id": self.client_id,
    #         "client_secret": self.client_secret,
    #         "redirect_uri": self.redirect_uri,
    #         "code": authorization_code,
    #     }
    #     response = requests.post(token_endpoint, data=data)
    #     if response.status_code == 200:
    #         access_token = response.json().get("access_token")
    #         self.access_token = access_token

    # def call_api(self, endpoint):
    #     headers = {
    #         "Authorization": f"Bearer {self.access_token}",
    #         "Content-Type": "application/json",
    #     }
    #     response = requests.get(endpoint, headers=headers)
    #     # Handle the API response

    def _get_company_domain(self):
        """Add company related domain for export product # T-02039"""
        domain = [
            "|",
            ("company_id", "=", self.company_id.id),
            ("company_id", "=", False),
        ]
        return domain

    def generate_token(self):
        """Generate token for Clickup."""
        self.ensure_one()
        authorization_url = self.get_authorization_url()
        params = {
            "type": "ir.actions.client",
            "tag": "redirect_with_code",
            "url": authorization_url,
        }
        return params

    def get_authorization_url(self):
        redirect_uri = (
            http.request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        )
        # redirect_uri = "https://app.clickup.com"
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": "read",
            "redirect_uri": redirect_uri,
        }
        authorization_url = "https://app.clickup.com/api?" + urlencode(params)

        return authorization_url

    # @http.route("/callback", type="http", auth="public", methods=["GET"])
    # def handle_callback(self, **kwargs):
    #     authorization_code = self.extract_authorization_code(
    #         http.request.httprequest.url
    #     )

    #     self.exchange_authorization_code(authorization_code)
    #     # Redirect to a success page or perform any additional actions
    #     return _("Authorization code exchange successful")

    # def extract_authorization_code(self, url):
    #     parsed_url = urlparse(url)
    #     query_params = parse_qs(parsed_url.query)
    #     authorization_code = query_params.get("code", [""])[0]
    #     return authorization_code

    # def exchange_authorization_code(self, authorization_code):
    #     token_endpoint = "https://api.clickup.com/api/v2/oauth/token"
    #     data = {
    #         "client_id": self.client_id,
    #         "client_secret": self.client_secret,
    #         "code": authorization_code,
    #     }
    #     response = requests.post(token_endpoint, data=data)
    #     if response.status_code == 200:
    #         response.json().get("access_token")


class ClickupBackendAdapter(Component):
    _name = "clickup.backend.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.backend"
