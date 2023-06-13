import json
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from odoo.addons.queue_job.job import identity_exact
from odoo import fields, models

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

    name = fields.Char(string="Clickup Backend ID", required=True)

    # Live
    api_key = fields.Char(string="API Key/Token", required=True)
    uri = fields.Char(string="URI/Location", required=True)

    # Test
    test_mode = fields.Boolean(string="Test Mode", default=True)
    test_token = fields.Char(string="Test API Key/Token")
    test_location = fields.Char(string="Test URI/Location")

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
                backend[from_date_field]
            search_dict = filters.get("search", {})

            if model in [
                "clickup.project.project",
                "clickup.project.tasks",
                "clickup.project.task.type",
            ]:
                to_date = import_start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                to_date = to_iso_datetime(import_start_time)

            if not search_dict.get("updated"):
                search_dict["updated"] = []

            search_dict["updated"].append(
                {"operator": "<", "value": to_date, "action": "import"}
            )

            filters["search"] = json.dumps(search_dict)
            # filters["limit"] = backend.limit
            filters["with_count"] = "true"
            force = False
            if force_update_field:
                force = backend[force_update_field]
            if model == "clickup.project.project":
                job_options["description"] = "Prepare jobs for clickup Project import"
            if model == "clickup.project.tasks":
                job_options["description"] = "Prepare jobs for clickup Task import"
            if model == "clickup.project.task.type":
                job_options["description"] = "Prepare jobs for clickup Stage import"
            clickup_model = (
                self.env[model].with_delay(**job_options or {})
                if with_delay
                else self.env[model]
            )

            clickup_model.import_batch(
                backend,
                filters=filters,
                force=force,
                **{"no_delay": not with_delay},
                job_options=job_options,
            )
            if force:
                backend[force_update_field] = False
        next_time = import_start_time - timedelta(seconds=IMPORT_DELTA_BUFFER)
        if from_date_field:
            self.write({from_date_field: next_time})

    def import_projects(self, with_delay=True, from_sync=False):
        """#T-02421 Import Clickup References"""

        for backend in self:
            backend._import_from_date(
                model="clickup.project.project",
                from_date_field=None if not from_sync else False,
                priority=0,
                with_delay=with_delay,
            )

    def import_tasks(self, with_delay=True, from_sync=False):
        for backend in self:
            backend._import_from_date(
                model="clickup.project.tasks",
                from_date_field=None if not from_sync else False,
                priority=0,
                with_delay=with_delay,
            )

    def import_stages(self, with_delay=True, from_sync=False):
        for backend in self:
            backend._import_from_date(
                model="clickup.project.task.type",
                from_date_field=None if not from_sync else False,
                priority=0,
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

        clickup_location = ClickupLocation(
            location=location, token=token, model=model_name
        )

        # clickup have different endpoint/credentials for token
        clickup_location_token = ClickupTokenLocation(
            location=location, model=model_name
        )
        with ClickupAPI(
            clickup_location, clickup_location_token, model=model_name
        ) as clickup_api:
            _super = super(ClickupBackend, self)
            # from the components we'll be able to do: self.work.clickup_api
            with _super.work_on(model_name, clickup_api=clickup_api, **kwargs) as work:
                yield work

    def export_projects(self, with_delay=True, from_sync=False):
        for backend in self.sudo():
            backend._export_from_date(
                model="clickup.project.project",
                from_date_field=None if not from_sync else False,
                with_delay=with_delay,
                identity_key=identity_exact,
            )

    def export_tasks(self, with_delay=True, from_sync=False):
        for backend in self.sudo():
            backend._export_from_date(
                model="clickup.project.tasks",
                from_date_field=None if not from_sync else False,
                with_delay=with_delay,
                identity_key=identity_exact,
            )

    def _export_from_date(
        self,
        model,
        from_date_field=None,
        filters=None,
        force_update_field=None,
        priority=None,
        identity_key=identity_exact,
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
            search_dict = filters.get("search", {})
            if from_date:
                # T-02383: clickup accepts different date time format
                # for category and variant.
                if model in [
                    "akeneo.product.category",
                    "akeneo.attribute",
                    "akeneo.reference",
                    "akeneo.product.product.image",
                ]:
                    from_date = from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                else:
                    from_date = to_iso_datetime(from_date)
                search_dict.update(
                    {
                        "updated": [
                            {"operator": ">", "value": from_date, "action": "export"}
                        ]
                    }
                )
            if model != "akeneo.attribute":
                if model in [
                    "clickup.project.project",
                    "clickup.project.tasks",
                    "clickup.project.task.type",
                ]:
                    to_date = import_start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                else:
                    to_date = to_iso_datetime(import_start_time)

                if not search_dict.get("updated"):
                    search_dict["updated"] = []

                search_dict["updated"].append(
                    {"operator": "<", "value": to_date, "action": "export"}
                )

            filters["search"] = json.dumps(search_dict)
            # filters["limit"] = backend.limit
            filters["with_count"] = "true"
            force = False
            if force_update_field:
                force = backend[force_update_field]
            if model == "clickup.project.project":
                job_options["description"] = "Prepare jobs for clickup Project Export"
            if model == "clickup.project.tasks":
                job_options["description"] = "Prepare jobs for clickup Task Export"
            if model == "clickup.project.task.type":
                job_options["description"] = "Prepare jobs for clickup Stage Export"
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

    def test_cron_import_clickup_changes(
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

    def test_cron_export_clickup_changes(
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
