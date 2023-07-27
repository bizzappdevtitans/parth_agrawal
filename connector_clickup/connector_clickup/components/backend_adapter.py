import logging
import socket
import urllib
from datetime import datetime

import requests
from simplejson.errors import JSONDecodeError

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import InvalidDataError, NetworkRetryableError
from odoo.addons.queue_job.exception import RetryableJobError

_logger = logging.getLogger(__name__)


class ClickupTokenLocation:
    """Class hold the credentials needs to send request to get Token"""

    def __init__(
        self,
        location,
        url_path,
        version,
        client_id,
        client_secret,
        auth_code,
    ):
        """Initializes a ClickupTokenLocation object."""
        self._location = "{}/api/{}/oauth/".format(url_path, version)
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_code = auth_code

    @property
    def location(self):
        """Token location of the Clickup"""
        return self._location


class ClickupLocation:
    """Class holds all the credentials needs for successful remote call"""

    def __init__(self, location, token, url_path, version):
        """Initializes a ClickupLocation object."""
        self._location = location
        self.token = token
        self.url_path = url_path
        self.version = version

    @property
    def location(self):
        """Main location of the Clickup"""
        location = "{}/api/{}".format(self.url_path, self.version)
        return location


class ClickupTokenClient:
    """Main class responsible to sends request/get response (For Token)"""

    def __init__(self, location, client_id, client_secret, auth_code):
        """Initializes a ClickupTokenClient object."""
        self._location = location
        self._client_id = client_id
        self._client_secret = client_secret
        self._auth_code = auth_code

    def get_data(self):
        """Get the token grant credentials"""
        data = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "code": self._auth_code,
        }
        return data

    def call(self, arguments=None, http_method=None, resource_path=None):
        """Call method for the Token API execution with all headers and parameters."""
        url = self._location + resource_path
        if http_method is None:
            http_method = "post"
        function = getattr(requests, http_method)
        headers = self.get_data()
        kwargs = {"headers": headers}
        if http_method == "post":
            kwargs["json"] = arguments
        res = function(url, headers)
        if res.status_code == 400 and res.content:
            raise requests.HTTPError(
                url, res.status_code, res.content, headers, __name__
            )
        res.raise_for_status()
        return res.json()


class ClickupClient:
    """
    Class responsible to send/get request/response to/from remote system
    respectively
    """

    def __init__(
        self,
        location,
        token,
    ):
        """Initializes a ClickupClient object."""
        self._location = location
        self._token = token

    def get_header(self):
        """Headers for the clickup api"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": self._token,
        }
        return headers

    def call(self, arguments=None, http_method=None, resource_path=None, headers=None):
        """Call method for the Token API execution with all headers and parameters."""
        if resource_path is None:
            _logger.exception("Remote System API called without resource path")
            raise NotImplementedError
        url = self._location + resource_path
        if http_method is None:
            http_method = "get"
        function = getattr(requests, http_method)
        headers = self.get_header()
        kwargs = {"headers": headers}
        if arguments and arguments.get("next_url"):
            url = arguments.pop("next_url")
        if http_method == "get":
            kwargs["params"] = arguments
        elif arguments is not None:
            kwargs["json"] = arguments
        res = function(url, **kwargs)
        try:
            results = res.json()
        except JSONDecodeError as err:
            raise InvalidDataError from err(
                url, res.status_code, res._content, headers, __name__
            )
        if res.status_code == 200:
            if res._content:
                if results.get("errors"):
                    raise InvalidDataError(
                        url,
                        res.status_code,
                        results.get("errors"),
                        __name__,
                    )
        elif res.status_code == 400 or res._content:
            raise InvalidDataError(
                url, res.status_code, res._content, headers, __name__
            )
        elif res.status_code == 404 or results.get("status") == 404:
            raise InvalidDataError(
                url, res.status_code, res._content, headers, __name__
            )
        res.raise_for_status()
        return results


class ClickupAPI:
    def __init__(self, location, location_token):
        """Initializes a ClickupAPI object."""
        self.location = location
        self._api = None
        self._api_token = None
        self._location_token = location_token

    @property
    def api(self):
        """Config the API values"""
        if self._api is None:
            clickup_client = ClickupClient(
                self.location.location,
                self.location.token,
            )
            self._api = clickup_client
        return self._api

    @property
    def api_token(self):
        """Config the API token values"""
        if self._api_token is None:
            clickup_token_client = ClickupTokenClient(
                self._location_token.location,
                self._location_token.client_id,
                self._location_token.client_secret,
                self._location_token.auth_code,
            )
            self._api_token = clickup_token_client
        return self._api_token

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
            return result
        except (socket.gaierror, OSError, socket.timeout) as err:
            raise NetworkRetryableError from err(
                "A network error caused the failure of the job: " "%s" % err
            )
        except urllib.error.HTTPError as err:
            if err.code in [502, 503, 504]:
                # Origin Error
                raise RetryableJobError from err(
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
    """External Records Adapter for Clickup"""

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

    def read(self, external_id, attributes=None):
        """Returns the information of a record"""
        raise NotImplementedError

    def create(self, data):
        """Create a record on the external system"""
        raise NotImplementedError

    def write(self, external_id, data):
        """Update records on the external system"""
        raise NotImplementedError

    def delete(self, external_id):
        """Delete a record on the external system"""
        raise NotImplementedError

    def get_token(self, arguments=None, http_method=None):
        """Method to get token from remote system"""
        return self._call(
            resource_path="token",
            arguments=arguments,
            http_method=http_method,
            is_token=True,
        )

    def get_team(self, arguments=None, http_method=None):
        """Method to get team id from remote system"""
        return self._call(
            resource_path="/team",
            arguments=arguments,
            http_method="get",
            is_token=False,
        )

    def get_chat(self, arguments=None, http_method=None, resource_path=None):
        """Method to get chats from remote system"""
        return self._call(
            resource_path=resource_path,
            arguments=arguments,
            http_method="get",
            is_token=False,
        )

    def set_checklist(self, arguments=None, http_method=None, resource_path=None):
        """Method to get chats from remote system"""
        return self._call(
            resource_path=resource_path,
            arguments=arguments,
            http_method="put",
            is_token=False,
        )

    def _call(self, resource_path, arguments=None, http_method=None, is_token=False):
        """Use clickup api attribute for call method execution"""
        try:
            clickup_api = getattr(self.work, "clickup_api", None)
        except AttributeError as err:
            raise AttributeError from err(
                "You must provide a clickup_api attribute with a "
                "ClickupAPI instance to be able to use the "
                "Backend Adapter."
            )
        return clickup_api.call(
            resource_path, arguments, http_method=http_method, is_token=is_token
        )


class GenericAdapter(AbstractComponent):
    # pylint: disable=method-required-super

    _name = "clickup.adapter"
    _inherit = "clickup.crud.adapter"
    _odoo_ext_id_key = "external_id"
    _last_update_date = "date_updated"
    _clickup_model = None
    _clickup_ext_id_key = "uuid"

    def search(self, filters=None):
        """
        Returns the information of a record
        :rtype: dict
        """
        resource_path = self._clickup_model
        result = self._call(resource_path, arguments=filters)
        return result

    def search_read(self, filters=None):
        """
        Search records according to some criteria
        and returns their information
        """
        resource_path = self._clickup_model
        result = self._call(resource_path, arguments=filters)
        return result

    def read(self, external_id=None, attributes=None):
        """Returns the information of a record
        :rtype: dict
        """
        resource_path = self._clickup_model
        if external_id:
            resource_path = "{}/{}".format(resource_path, external_id)
        result = self._call(resource_path)
        return result

    def create(self, data):
        """Create a record on the external system"""
        resource_path = self._clickup_model
        result = self._call(resource_path, data, http_method="post")
        return result

    def write(self, external_id, data):
        """Update records on the external system"""
        resource_path = "{}/{}".format(self._clickup_model, external_id)
        result = self._call(resource_path, data, http_method="put")
        return result

    def delete(self, external_id):
        """Delete a record on the external system"""
        resource_path = self._clickup_model
        resource_path = "{}/{}".format(resource_path, external_id)
        result = self._call(resource_path, http_method="delete")
        return result
