import base64
import logging
import re
import time
import urllib

from selenium import webdriver

logging.basicConfig(level=logging.INFO)


class OAuth2Client:
    def __init__(
        self,
        client_id,
        client_secret,
        version,
        redirect_uri,
        scopes,
        web_endpoint=None,
        api_endpoint=None,
        username=None,
        password=None,
        test_mode=False,
    ):
        self.scopes = "read"
        self.username = username
        self.password = password
        self.client_secret = client_secret
        self.client_id = client_id

        self.redirect_uri = "https://app.clickup.com"
        if not web_endpoint:
            web_endpoint = "https://app.clickup.com/api"
        self.web_endpoint = web_endpoint
        if not api_endpoint:
            # version = v1
            api_endpoint = "https://api.clickup.com/api/v2/oauth/token"

        self.api_endpoint = api_endpoint
        self.access_token = None
        self.access_token_expiry = None
        self.refresh_token = None
        self.refresh_token_expiry = None

    def credential_list(self):
        return []

    def get_user_access_scope(self, scopes):
        """Method to get the scopes."""
        scope = scopes.split("scope=")
        # if not len(scope):
        #     logging.error("Unidentified value of scope")
        return scope[-1]

    def get_application_scopes(self):
        # TODO : Have to support application scope in future
        return []

    def get_authorization_code(self, signin_url):
        # firefox_options = webdriver.FirefoxOptions()
        # firefox_options.add_argument("-headless")
        # print(firefox_options)
        # firefox_service = webdriver.firefox.service.Service(
        #     "/home/bizzappdev/geckodriver"
        # )
        # print(firefox_service)
        # firefox_service.start()
        # print(firefox_service)
        # print("Firefox service started")

        # firefox_driver = webdriver.Firefox(
        #     service=firefox_service, options=firefox_options
        # )

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("-headless")

        chrome_service = webdriver.chrome.service.Service(
            executable_path="/home/bizzappdev/chromedriver"
        )

        chrome_driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        try:
            chrome_driver.get(signin_url)
            time.sleep(10)

            chrome_driver.find_element_by_name("Connect").click()
            time.sleep(5)

            url = chrome_driver.current_url

        finally:
            chrome_driver.quit()

        if "code=" in url:
            code = re.findall("code=(.*?)&", url)[0]
            logging.info("Code Obtained: %s", code)
        else:
            logging.error("Unable to obtain code via sign-in URL")

        decoded_code = urllib.parse.unquote(code)
        if not isinstance(decoded_code, str):
            decoded_code = decoded_code.decode("utf8")

        return decoded_code

    # def get_authorization_code(self, signin_url):
    #     # options = webdriver.FirefoxOptions()
    #     # print("options", options)
    #     # driver = webdriver.Firefox(options=options)
    #     # print("driver", driver)
    #     browser = webdriver.Firefox()
    #     browser.get(signin_url)
    #     time.sleep(10)
    #     form_userid = browser.find_element("name", "userid")
    #     form_userid.send_keys(self.username)
    #     browser.find_element("name", "signin-continue-btn").click()
    #     time.sleep(5)
    #     form_pw = browser.find_element("name", "pass")
    #     time.sleep(10)
    #     form_pw.send_keys(self.password)
    #     time.sleep(5)
    #     browser.find_element("name", "sgnBt").click()
    #     time.sleep(5)
    #     url = browser.current_url
    #     browser.quit()
    #     if "code=" in url:
    #         code = re.findall("code(.*?)&", url)[0]
    #         logging.info("Code Obtained: %s", code)
    #     else:
    #         logging.error("Unable to obtain code via sign in URL")

    #     decoded_code = urllib.parse.unquote(code)
    #     if not isinstance(decoded_code, str):
    #         decoded_code = decoded_code.decode("utf8")
    #     return decoded_code

    def get_user_authorization_url(self):
        if not self.client_id or not self.redirect_uri or not self.scopes:
            logging.error("Required parameter are missing for the authorization url!")
        param = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.scopes,
        }

        query = urllib.parse.urlencode(param)
        auth_url = "{}?{}".format(self.web_endpoint, query)

        return auth_url

    def _generate_request_headers(self, **kwargs):
        client_id = self.client_id or ""
        client_secret = self.client_secret or ""
        b64_encoded_credential = "{}:{}".format(client_id, client_secret)
        authorization_code = base64.b64encode(b64_encoded_credential.encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic {}".format(authorization_code),
        }

        return headers

    def _generate_application_request_body(self, **kwargs):
        body = {
            "grant_type": "client_credentials",
            "redirect_uri": self.redirect_uri,
            "scope": self.scopes,
        }

        return body

    def _generate_oauth_request_body(self, code, **kwargs):
        body = {
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
        }
        return body

    def _generate_refresh_request_body(self, **kwargs):
        if self.refresh_token is None:
            logging.error(
                "credential object does not contain refresh_token and/or scopes"
            )
        body = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "scope": self.scopes,
        }
        return body
