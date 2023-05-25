import logging
import socket
import urllib
from datetime import datetime

import requests

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import NetworkRetryableError
from odoo.addons.queue_job.exception import RetryableJobError

# from simplejson.errors import JSONDecodeError


_logger = logging.getLogger(__name__)


class ClickupTokenLocation(object):
    """Class hold the credentials needs to send request to get Token"""

    def __init__(self, location, model):
        self._location = location

    @property
    def location(self):
        """Token location of the Akeneo"""
        return self._location


class ClickupLocation(object):
    """Class holds all the credentials needs for successful remote call"""

    def __init__(self, location, token, model):
        self._location = location
        self.token = token
        self.model = model

    @property
    def location(self):
        """Main location of the Akeneo"""
        location = "https://api.clickup.com/api/v2/folder/{location}/list".format(
            location=self._location
        )
        return location


class ClickupClient(object):
    """
    Class responsible to send/get request/response to/from remote system
    respectively
    """

    def __init__(
        self,
        location,
        token,
        model,
    ):
        self._location = location
        self._token = token
        self._model = model

    def get_header(self):
        """Headers for the akeneo api"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % (self._token),
        }
        return headers

    def call(self, resource_path, arguments, http_method=None):
        """send/get request/response to/from remote system"""
        if self._model == "clickup.project.project":
            url = self._location
            headers = {"Authorization": self._token}

            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                return data.get("lists", [])
            except requests.exceptions.RequestException as e:
                _logger.error("Failed to fetch projects from ClickUp API: %s", str(e))
                return []

        if self._model == "clickup.project.tasks":
            url = self._location
            headers = {"Authorization": self._token}

            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                data.get("lists", [])

                all_tasks = []

                for project in data["lists"]:
                    clickup_project_id = project["id"]

                    list_id = clickup_project_id
                    url = "https://api.clickup.com/api/v2/list/" + list_id

                    headers = {"Authorization": self._token}

                    response = requests.get(url, headers=headers)

                    data = response.json()

                    tasks_url = "https://api.clickup.com/api/v2/list/{}/task".format(
                        list_id
                    )
                    tasks_response = requests.get(tasks_url, headers=headers)
                    tasks_data = tasks_response.json()

                    all_tasks.extend(tasks_data["tasks"])

                return all_tasks
            except requests.exceptions.RequestException as e:
                _logger.error("Failed to fetch projects from ClickUp API: %s", str(e))
                return []


class ClickupAPI(object):
    def __init__(self, location, token, model):
        self.location = location
        self._token = token
        self.model = model
        self._api = None

    @property
    def api(self):
        """Config the API values"""
        if self._api is None:
            akeneo_client = ClickupClient(
                self.location.location,
                self.location.token,
                self.location.model,
            )
            self._api = akeneo_client

        return self._api

    # def call(self, params=None, data=None):
    #     url = f"https://api.clickup.com/api/v2/folder/{self.uri}/list"
    #     headers = {"Authorization": self.api_key}
    #     try:
    #         response = requests.get(url, headers=headers, params=params, json=data)
    #         response.raise_for_status()
    #         data = response.json()
    #         return data.get("lists", [])
    #     except requests.exceptions.RequestException as e:
    #         _logger.error("Failed to fetch projects from ClickUp API: %s", str(e))
    #         return []
    def api_call(self, resource_path, arguments, http_method=None, is_token=False):
        """Adjust available arguments per API"""
        api = False
        if is_token:
            api = self.api_token
        else:
            api = self.api

        if not api:
            return api
        return api.call(
            resource_path=resource_path, arguments=arguments, http_method=http_method
        )

    def call(self, resource_path, arguments, http_method=None, is_token=False):
        """send/get request/response to/from remote system"""
        try:
            start = datetime.now()
            try:
                result = self.api_call(
                    resource_path=resource_path,
                    arguments=arguments,
                    http_method=http_method,
                    is_token=is_token,
                )
            except Exception:
                api_name = is_token and "api_token" or "api"
                _logger.error(
                    "%s.call('%s', %s) failed", api_name, resource_path, arguments
                )
                raise
            else:
                api_name = is_token and "api_token" or "api"
                _logger.debug(
                    "%s.call('%s', %s) returned %s in %s seconds",
                    api_name,
                    resource_path,
                    arguments,
                    result,
                    (datetime.now() - start).seconds,
                )
            # Un-comment to record requests/responses in ``recorder``
            # record(method, arguments, result)
            return result
        except (socket.gaierror, socket.error, socket.timeout) as err:
            raise NetworkRetryableError(
                "A network error caused the failure of the job: " "%s" % err
            )
        except urllib.error.HTTPError as err:
            if err.code in [502, 503, 504]:
                # Origin Error
                raise RetryableJobError(
                    "HTTP Error:\n"
                    "Code: %s\n"
                    "Reason: %s\n"
                    "Headers: %d\n" % (err.code, err.reason, err.headers)
                )
            else:
                raise

    def __enter__(self):
        # Return the object to be used in the `with` statement
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Cleanup logic if needed
        pass


class ClickupCRUDAdapter(AbstractComponent):
    """External Records Adapter for Magento"""

    # pylint: disable=method-required-super

    _name = "clickup.crud.adapter"
    _inherit = ["base.backend.adapter", "base.clickup.connector"]
    _usage = "backend.adapter"

    def search(self, filters=None):
        """Search records according to some criterias
        and returns a list of ids"""
        raise NotImplementedError

    def search_read(self, filters=None):
        """Search records according to some criterias
        and returns a list of ids"""
        raise NotImplementedError

    # def read(self, external_id, attributes=None, storeview=None):
    #     """Returns the information of a record"""
    #     raise NotImplementedError

    def _call(self, method, arguments=None, http_method=None, storeview=None):
        try:
            akeneo_api = getattr(self.work, "akeneo_api")  # noqa: B009
        except AttributeError:
            raise AttributeError(
                "You must provide a magento_api attribute with a "
                "MagentoAPI instance to be able to use the "
                "Backend Adapter."
            )
        return akeneo_api.call(method, arguments, http_method=http_method)


class GenericAdapter(AbstractComponent):
    # pylint: disable=method-required-super

    _name = "clickup.adapter"
    _inherit = "clickup.crud.adapter"
    _odoo_ext_id_key = "external_id"
    _akeneo_model = None
    _last_update_date = "updated"

    def search(self, filters=None):
        """
        Returns the information of a record

        :rtype: dict
        """
        resource_path = self._akeneo_model
        result = self._call(resource_path, arguments=filters)
        return result

    def search_read(self, filters=None):
        """
        Search records according to some criteria
        and returns their information
        """
        resource_path = self._akeneo_model
        result = self._call(resource_path, arguments=filters)
        return result
