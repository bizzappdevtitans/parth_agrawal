import json
import logging
from datetime import datetime, timedelta

import requests

from ...models.clickup_oauth import oauth2_client


class ClickupOauthClient(oauth2_client.OAuth2Client):
    def exchange_code_for_access_token(self, **kwargs):
        logging.info("Trying to get a new user access token ... ")
        signin_url = self.get_user_authorization_url()
        code = self.get_authorization_code(signin_url)
        headers = self._generate_request_headers()
        body = self._generate_oauth_request_body(code=code)
        resp = requests.post(self.api_endpoint, data=body, headers=headers, timeout=10)
        content = json.loads(resp.content)
        if resp.status_code == requests.codes.ok:
            self.access_token = content["access_token"]
            self.access_token_expiry = (
                datetime.utcnow()
                + timedelta(seconds=int(content["expires_in"]))
                - timedelta(minutes=5)
            )
            self.refresh_token = content["refresh_token"]
            self.refresh_token_expiry = (
                datetime.utcnow()
                + timedelta(seconds=int(content["refresh_token_expires_in"]))
                - timedelta(minutes=5)
            )
        else:
            logging.error(
                "Unable to retrieve token.  Status code: %s - %s",
                resp.status_code,
                requests.status_codes._codes[resp.status_code],
            )
            logging.error(
                "Error: %s - %s", content["error"], content["error_description"]
            )

    def get_access_token(self, **kwargs):
        """
        refresh token call
        """
        # logging.info("Trying to get a new user access token ... ")
        # headers = self._generate_request_headers()
        # body = self._generate_refresh_request_body()
        # resp = requests.post(self.api_endpoint, data=body, headers=headers)
        # content = json.loads(resp.content)
        # self.token_response = content

        # if resp.status_code == requests.codes.ok:
        #     self.access_token = content["access_token"]
        #     self.token_expiry = (
        #         datetime.utcnow()
        #         + timedelta(seconds=int(content["expires_in"]))
        #         - timedelta(minutes=5)
        #     )
        # else:
        #     logging.error(
        #         "Unable to retrieve token.  Status code: %s - %s",
        #         resp.status_code,
        #         requests.status_codes._codes[resp.status_code],
        #     )
        #     logging.error(
        #         "Error: %s - %s", content["error"], content["error_description"]
        #     )

        signin_url = self.get_user_authorization_url()
        code = self.get_authorization_code(signin_url)
        headers = self._generate_request_headers()
        body = self._generate_oauth_request_body(code=code)
        resp = requests.post(self.api_endpoint, data=body, headers=headers, timeout=10)
        content = json.loads(resp.content)
        if resp.status_code == requests.codes.ok:
            self.access_token = content["access_token"]
            self.access_token_expiry = (
                datetime.utcnow()
                + timedelta(seconds=int(content["expires_in"]))
                - timedelta(minutes=5)
            )
            self.refresh_token = content["refresh_token"]
            self.refresh_token_expiry = (
                datetime.utcnow()
                + timedelta(seconds=int(content["refresh_token_expires_in"]))
                - timedelta(minutes=5)
            )
        else:
            logging.error(
                "Unable to retrieve token.  Status code: %s - %s",
                resp.status_code,
                requests.status_codes._codes[resp.status_code],
            )
            logging.error(
                "Error: %s - %s", content["error"], content["error_description"]
            )

    def get_application_token(self, **kwargs):
        """
        makes call for application token and stores result in credential object
        returns credential object
        """
        logging.info("Trying to get a new application access token ... ")
        headers = self._generate_request_headers()
        body = self._generate_application_request_body()
        resp = requests.post(self.api_endpoint, data=body, headers=headers, timeout=10)
        content = json.loads(resp.content)
        if resp.status_code == requests.codes.ok:
            self.access_token = content["access_token"]
            # set token expiration time 5 minutes before actual expire time
            self.token_expiry = (
                datetime.utcnow()
                + timedelta(seconds=int(content["expires_in"]))
                - timedelta(minutes=5)
            )

        else:
            logging.error(
                "Unable to retrieve token.  Status code: %s - %s",
                resp.status_code,
                requests.status_codes._codes[resp.status_code],
            )
            logging.error(
                "Error: %s - %s", content["error"], content["error_description"]
            )


# ebay = ClickupOauthClient(
#     client_id="BC9ZMQBCTNTUPKKFDKIWVTTVU4PIIB1P",
#     client_secret="WGP7BPW7FWAW3212T47ANB5HENVFV6Y7J35I1CT69T7K18MI2RY1Q35SWWOKRU3J",
#     version=None,
#     redirect_uri="https://aap.clickup.com",
#     scopes="read",
#     username="parth.agrawal@bizzappdev.com",
#     password="Parth123!@#",
#     test_mode=False,
# )
# ebay.exchange_code_for_access_token()
# access_token = ebay.access_token
# headers = {
#     "Content-Type": "application/json",
#     "Authorization": "Bearer %s" % (access_token),
# }
# print(headers)
# res = requests.get(
#     "https://api.sandbox.ebay.com/sell/fulfillment/v1/order", headers=headers
# )
# print(ebay.access_token, ebay.refresh_token)

ebay = ClickupOauthClient(
    client_id="BC9ZMQBCTNTUPKKFDKIWVTTVU4PIIB1P",
    client_secret="WGP7BPW7FWAW3212T47ANB5HENVFV6Y7J35I1CT69T7K18MI2RY1Q35SWWOKRU3J",
    version=None,
    redirect_uri="https://aap.clickup.com",
    scopes="read",
    username="parth.agrawal@bizzappdev.com",
    password="Parth123!@#",
    test_mode=False,
)
ebay.get_access_token()
access_token = ebay.access_token
