import json
import logging
import socket
import urllib
from datetime import datetime

import requests

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import InvalidDataError, NetworkRetryableError
from odoo.addons.queue_job.exception import RetryableJobError

MAGENTO_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
from simplejson.errors import JSONDecodeError

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
        location = "https://api.clickup.com/api/v2"
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
            "Authorization": "%s" % (self._token),
        }
        return headers

    def call(self, arguments=None, http_method=None, resource_path=None, headers=None):
        """Call method for the Token API execution with all headers and parameters."""
        search_json = arguments.get("search")
        search_dict = json.loads(search_json) if search_json else {}
        search_dict.get("updated", [{}])[0].get("action")

        url = self._location + resource_path

        if http_method is None:
            http_method = "get"
        function = getattr(requests, http_method)
        default_headers = self.get_header()

        if headers:
            default_headers.update(headers)
        kwargs = {"headers": default_headers}
        if http_method == "get":
            kwargs["params"] = arguments
        elif isinstance(arguments, str):
            kwargs["data"] = arguments
        elif arguments is not None:
            kwargs["json"] = arguments
        res = function(url, **kwargs)
        # Exceptional Case: status-code 202 is consider as error by raise_for_status

        if res.status_code == 202:
            if res._content:
                try:
                    result = res.json()
                    if result.get("errors"):
                        raise InvalidDataError(
                            url,
                            res.status_code,
                            result.get("errors"),
                            __name__,
                        )
                except JSONDecodeError:
                    _logger.warning(
                        "\n Invalid json payload received :%s \n" % (res._content)
                    )
                    return res._content
            return True
        # Exceptional Case: status-code 201 is consider as error by raise_for_status
        if res.status_code == 201:
            if res._content:
                try:
                    return res.json()
                except JSONDecodeError:
                    _logger.warning(
                        "\n Invalid json payload received :%s \n" % (res._content)
                    )
                    return res._content
            return res._content
        if res.status_code == 400 and res._content:
            # From remote system on invalid data we get 400 error
            # but raise_for_status treats it as network error(which is retryable)
            raise InvalidDataError(
                url, res.status_code, res._content, headers, __name__
            )
        if res.status_code == 404 and res.json().get("status") == 404:
            # In case record(product/shipment/DO) not exists in remote system
            raise InvalidDataError(
                url, res.status_code, res._content, headers, __name__
            )
        res.raise_for_status()
        try:
            result = res.json()

            return result
        except JSONDecodeError:
            _logger.warning("\n Everstox Response Content :%s \n" % (res._content))
            return res._content


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

    def _call(self, resource_path, arguments=None, http_method=None, storeview=None):
        try:
            akeneo_api = getattr(self.work, "akeneo_api")  # noqa: B009
        except AttributeError:
            raise AttributeError(
                "You must provide a magento_api attribute with a "
                "MagentoAPI instance to be able to use the "
                "Backend Adapter."
            )
        return akeneo_api.call(resource_path, arguments, http_method=http_method)


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

    def read(self, external_id=None, attributes=None):
        """Returns the information of a record

        :rtype: dict
        """
        resource_path = self._akeneo_model
        if external_id:
            resource_path = "{}/{}".format(resource_path, external_id)
        result = self._call(resource_path)
        return result

    def create(self, data):
        """Create a record on the external system"""

        resource_path = self._akeneo_model
        result = self._call(resource_path, data, http_method="post")
        return result

    def write(self, external_id, data):
        """Update records on the external system"""

        resource_path = self._akeneo_model
        # resource_path = "{}/{}".format(resource_path, external_id)
        # if self._remote_model_extension:
        #     resource_path = "{}/{}".format(resource_path, self._remote_model_extension)

        result = self._call(resource_path, data, http_method="put")
        return result

    def delete(self, external_id):
        """Delete a record on the external system"""
        resource_path = self._akeneo_model
        resource_path = "{}/{}".format(resource_path, external_id)
        result = self._call(resource_path, http_method="delete")
        return result
