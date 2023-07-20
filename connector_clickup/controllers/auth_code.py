from werkzeug.utils import redirect

from odoo import http
from odoo.http import request


class ClickUpOAuthController(http.Controller):
    @http.route(
        "/clickup/oauth/callback",
        type="http",
        auth="public",
        website=False,
    )
    def clickup_oauth_callback(self, **kwargs):
        # Retrieve the code parameter from the query string

        code = kwargs.get("code")

        # Retrieve the backend record ID
        backend_id = int(kwargs.get("state"))
        # Find the backend record by the ID
        backend = request.env["clickup.backend"].browse(backend_id)

        if backend:
            if backend.test_mode:
                backend.auth_code_test = code
            else:
                backend.auth_code = code

        # Redirect the user to a success page or any other page you desire
        return redirect("/web#model=clickup.backend&view_type=form&id=%s" % backend_id)
