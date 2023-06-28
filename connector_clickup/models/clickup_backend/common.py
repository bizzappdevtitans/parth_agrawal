import logging
from contextlib import contextmanager
from datetime import datetime, timedelta

from odoo import fields, models

from odoo.addons.component.core import Component

# from ...components.backend_adapter import ClickUpBackendAdapter
from ...components.backend_adapter import (
    ClickupAPI,
    ClickupLocation,
    ClickupTokenLocation,
)
from ...components.misc import to_iso_datetime

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
    datetime_filter_project = fields.Datetime()
    datetime_filter_task = fields.Datetime()
    limit = fields.Integer(default=100)
    force_update_projects = fields.Boolean()
    force_update_stages = fields.Boolean()
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
        job_options = {}
        if priority or priority == 0:
            job_options["priority"] = priority
        for backend in self:
            if from_date_field:
                from_date = backend[from_date_field]
                if from_date:
                    from_date = from_date.strftime("%Y-%m-%dT%H:%M:%SZ")

            filters["limit"] = backend.limit
            filters["with_count"] = "true"
            force = False
            if force_update_field:
                force = backend[force_update_field]

            model_parts = model.split(".")
            model_name = " ".join(part.title() for part in model_parts[1:])
            job_options["description"] = f"Prepare Batch To Import {model_name}"

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
                from_date_field="datetime_filter_project",
                priority=5,
                with_delay=with_delay,
                force_update_field="force_update_projects",
            )

    # def import_projects(self, with_delay=True):
    #     force = True
    #     for backend in self.sudo():
    #         self.env["clickup.project.project"].with_company(
    #             backend.sudo().company_id
    #         ).with_delay(priority=5).import_batch(backend=backend, force=force)

    def import_tasks(self, with_delay=True):
        for backend in self:
            backend._import_from_date(
                model="clickup.project.tasks",
                from_date_field="datetime_filter_task",
                priority=10,
                with_delay=with_delay,
            )

    def import_stages(self, with_delay=True):
        for backend in self:
            backend._import_from_date(
                model="clickup.project.task.type",
                from_date_field=None,
                priority=7,
                with_delay=with_delay,
            )

    @contextmanager
    def work_on(self, model_name, **kwargs):
        """Add the work on for clickup."""

        self.ensure_one()
        location = self.uri
        token = self.api_key
        if self.test_mode:
            location = self.test_location
            token = self.test_token

        clickup_location = ClickupLocation(location=location, token=token)

        # clickup have different endpoint/credentials for token
        clickup_location_token = ClickupTokenLocation(location=location)
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
            job_options["description"] = f"Prepare Batch To Export {model_name}"
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

    def generate_token(self):
        """Generate token for akeneo."""
        with self.work_on(self._name) as work:
            backend_adapter = work.component(usage="backend.adapter")
            token_dict = backend_adapter.get_token()
            token = token_dict.get("access_token")
            if self.test_mode:
                self.test_token = token
            else:
                self.api_key = token

    def _get_company_domain(self):
        """Add company related domain for export product # T-02039"""
        domain = [
            "|",
            ("company_id", "=", self.company_id.id),
            ("company_id", "=", False),
        ]
        return domain


class ClickupBackendAdapter(Component):
    _name = "clickup.backend.adapter"
    _inherit = "clickup.adapter"
    _apply_on = "clickup.backend"
