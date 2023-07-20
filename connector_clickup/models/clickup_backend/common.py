import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from urllib.parse import urlencode

from odoo import _, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component

from ...components.backend_adapter import (
    ClickupAPI,
    ClickupLocation,
    ClickupTokenLocation,
)
from ...components.misc import queue_job_description, to_iso_datetime

_logger = logging.getLogger(__name__)

IMPORT_DELTA_BUFFER = 30  # seconds

EXPORT_DELTA_BUFFER = 30  # seconds


class ClickupBackend(models.Model):
    _name = "clickup.backend"
    _inherit = "connector.backend"
    _description = "Clickup backend"

    name = fields.Char(required=True)
    auth_type = fields.Selection(
        [("api_key", "API Key"), ("Oauth", "Oauth Authentication")],
        required=True,
        default="api_key",
        help="""This will allow current backend to perform import export
        through selected authentication type""",
    )

    datetime_filter_task = fields.Datetime(
        help="""This will get all the tasks which is created
         or updated after your provided date and time"""
    )

    force_update_tasks = fields.Boolean()
    company_id = fields.Many2one(comodel_name="res.company", string="Company")

    team_id = fields.Char()
    redirect_url = fields.Char(
        help="""Enter that redirect url which is already set
        in clickup website's Clickup API app"""
    )
    # Live
    api_key = fields.Char(help="Enter API Key")
    uri = fields.Char(help="Enter End Point Location Of Space Id")
    client_id = fields.Char()
    client_secret = fields.Char()
    url_path = fields.Char(help="Enter the url path")
    version = fields.Selection(
        [("v2", "V2")],
        default="v2",
        help="""select the version for api url path""",
    )
    auth_code = fields.Char(
        help="""Auth code to generate access token""",
        readonly=True,
    )

    # Test
    test_mode = fields.Boolean(default=True)
    test_token = fields.Char()
    test_location = fields.Char()
    client_id_test = fields.Char()
    client_secret_test = fields.Char()
    url_path_test = fields.Char(help="Enter the url path")
    version_test = fields.Selection(
        [("v2", "V2")],
        default="v2",
        help="""select the version for api url path""",
    )
    auth_code_test = fields.Char(
        help="""Auth code to generate access token""",
        readonly=True,
    )

    def redirect_action(self):
        """Redirect to readme html file"""
        html_file_path = "/connector_clickup/static/src/README.html"

        return {
            "type": "ir.actions.act_url",
            "url": html_file_path,
            "target": "new",
        }

    def toggle_test_mode(self):
        """Switch between test mode and production mode"""
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
        filters.update({"to_date": import_start_time_new})
        job_options = {}
        if priority or priority == 0:
            job_options["priority"] = priority
        for backend in self:
            if from_date_field:
                from_date = backend[from_date_field]
                if from_date:
                    from_date = int(from_date.timestamp() * 1000)
                    filters.update({"from_date": from_date})

            force = False
            if force_update_field:
                force = backend[force_update_field]

            model_name = queue_job_description(self, model=model)
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

    def import_members(self, with_delay=True):
        """Import Clickup projects button action"""
        for backend in self:
            backend._import_from_date(
                model="clickup.res.users",
                from_date_field=None,
                priority=5,
                with_delay=with_delay,
                force_update_field=None,
            )

    def import_projects(self, with_delay=True):
        """Import Clickup projects button action"""
        for backend in self:
            backend._import_from_date(
                model="clickup.project.project",
                from_date_field=None,
                priority=5,
                with_delay=with_delay,
                force_update_field=None,
            )

    def import_tasks(self, with_delay=True):
        """Import Clickup tasks button action"""
        for backend in self:
            backend._import_from_date(
                model="clickup.project.task",
                from_date_field="datetime_filter_task",
                priority=10,
                with_delay=with_delay,
                force_update_field="force_update_tasks",
            )

    def import_stages(self, with_delay=True):
        """Import Clickup stages button action"""
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
        version = self.version
        client_id = self.client_id
        client_secret = self.client_secret
        token = self.api_key
        auth_code = self.auth_code
        url_path = self.url_path
        if self.test_mode:
            location = self.test_location
            version = self.version_test
            client_id = self.client_id_test
            client_secret = self.client_secret_test
            token = self.test_token
            auth_code = self.auth_code_test
            url_path = self.url_path_test

        clickup_location = ClickupLocation(
            location=location,
            token=token,
            version=version,
            url_path=url_path,
        )

        # Clickup have different endpoint/credentials for token
        clickup_location_token = ClickupTokenLocation(
            location=location,
            client_id=client_id,
            client_secret=client_secret,
            auth_code=auth_code,
            url_path=url_path,
            version=version,
        )
        with ClickupAPI(clickup_location, clickup_location_token) as clickup_api:
            _super = super()
            # from the components we'll be able to do: self.work.clickup_api
            with _super.work_on(model_name, clickup_api=clickup_api, **kwargs) as work:
                yield work

    def export_projects(self, with_delay=True, from_sync=False):
        """Export Clickup projects button action"""
        for backend in self.sudo():
            backend._export_from_date(
                model="clickup.project.project",
                from_date_field=None if not from_sync else False,
                priority=5,
                with_delay=with_delay,
            )

    def export_tasks(self, with_delay=True, from_sync=False):
        """Export Clickup tasks button action"""
        for backend in self.sudo():
            backend._export_from_date(
                model="clickup.project.task",
                from_date_field=None if not from_sync else False,
                priority=10,
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
        """Common method for export data from from_date."""

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

            model_name = queue_job_description(self, model=model)
            job_options["description"] = f"Export Batch of Clickup {model_name}"

            clickup_model = (
                self.env[model].with_delay(**job_options or {})
                if with_delay
                else self.env[model]
            )

            clickup_model.export_batch(
                backend,
                job_options=job_options,
                filters=filters,
            )

        next_time = import_start_time - timedelta(seconds=IMPORT_DELTA_BUFFER)
        if from_date_field:
            self.write({from_date_field: next_time})

    def cron_import_clickup_project_changes(
        self,
        filters=None,
        with_delay=True,
    ):
        """Scheduled action method of project import"""
        backends = self.env["clickup.backend"].search([])
        for backend in backends:
            backend.import_projects()

    def cron_import_clickup_stage_changes(
        self,
        filters=None,
        with_delay=True,
    ):
        """Scheduled action method of stage import"""
        backends = self.env["clickup.backend"].search([])

        for backend in backends:
            backend.import_stages()

    def cron_import_clickup_task_changes(
        self,
        filters=None,
        with_delay=True,
    ):
        """Scheduled action method of task import"""
        backends = self.env["clickup.backend"].search([])
        for backend in backends:
            backend.import_tasks()

    def cron_export_clickup_project_changes(
        self,
        filters=None,
        with_delay=True,
    ):
        """Scheduled action method of project export"""
        backends = self.env["clickup.backend"].search([])
        for backend in backends:
            backend.export_projects()

    def cron_export_clickup_task_changes(
        self,
        filters=None,
        with_delay=True,
    ):
        """Scheduled action method of task export"""
        backends = self.env["clickup.backend"].search([])
        for backend in backends:
            backend.export_tasks()

    def get_team_info(self):
        """Set team in team id field"""
        with self.work_on(self._name) as work:
            backend_adapter = work.component(usage="backend.adapter")
            team_id_dict = backend_adapter.get_team()
            teams = team_id_dict.get("teams", [])
            team = [team.get("id") for team in teams]
            self.team_id = ",".join(team)

    def _get_company_domain(self):
        """Add company related domain"""
        domain = [
            "|",
            ("company_id", "=", self.company_id.id),
            ("company_id", "=", False),
        ]
        return domain

    def generate_token(self):
        """Generate token for clickup."""
        required_fields = [
            "auth_code",
            "client_id",
            "client_secret",
            "version",
            "url_path",
        ]

        missing_fields = []

        if self.test_mode:
            test_required_fields = [field + "_test" for field in required_fields]
            missing_fields.extend(
                [field for field in test_required_fields if not getattr(self, field)]
            )
        else:
            missing_fields.extend(
                [field for field in required_fields if not getattr(self, field)]
            )

        if missing_fields:
            raise ValidationError(
                _(
                    "Please fill all the necessary fields: '{}' to generate access token"
                ).format(", ".join(missing_fields))
            )
        else:
            with self.work_on(self._name) as work:
                backend_adapter = work.component(usage="backend.adapter")
                token_dict = backend_adapter.get_token()
                token = token_dict.get("access_token")
                if self.test_mode:
                    self.test_token = token

                else:
                    self.api_key = token
            return self.get_team_info()

    def get_authorization_url(self):
        """Prepare the authorization url with parameters"""
        redirect_url = self.redirect_url

        if self.test_mode:
            client_id = self.client_id_test
        else:
            client_id = self.client_id
        backend_id = self.id
        params = {
            "state": backend_id,
            "client_id": client_id,
            "response_type": "code",
            "scope": "read",
            "redirect_uri": redirect_url + "/clickup/oauth/callback",
        }
        authorization_url = "https://app.clickup.com/api?" + urlencode(params)

        return authorization_url

    def generate_auth_code(self):
        """Generate token for Clickup."""
        self.ensure_one()
        required_fields = ["client_id", "client_secret", "redirect_url"]
        missing_fields = []

        if self.test_mode:
            test_required_fields = [
                "client_id_test",
                "client_secret_test",
                "redirect_url",
            ]
            missing_fields.extend(
                [field for field in test_required_fields if not getattr(self, field)]
            )
        else:
            missing_fields.extend(
                [field for field in required_fields if not getattr(self, field)]
            )

        if missing_fields:
            raise ValidationError(
                _(
                    "Please fill all the necessary fields: '{}' to generate access token"
                ).format(", ".join(missing_fields))
            )

        authorization_url = self.get_authorization_url()

        return {
            "type": "ir.actions.act_url",
            "url": authorization_url,
            "target": "new",
        }


class ClickupBackendAdapter(Component):
    _name = "clickup.backend.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.backend"
