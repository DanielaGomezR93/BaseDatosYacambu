# Part of odoo. See LICENSE file for full copyright and licensing details.
import json
import logging

import werkzeug.wrappers

from odoo import http
from odoo.exceptions import AccessError, AccessDenied
from odoo.http import request, Response

from odoo.addons.binaural_restful.common import invalid_response, valid_response

_logger = logging.getLogger(__name__)

expires_in = "yacambu_restful.access_token_expires_in"


class AccessToken(http.Controller):
    """."""

    def __init__(self):

        self._token = request.env["api.access_token"]
        self._expires_in = request.env.ref(expires_in).sudo().value

    @http.route("/api/auth/token", methods=["GET"], type="http", auth="none", csrf=False)
    def token(self, **post):
        _token = request.env["api.access_token"]
        params = ["db", "login", "password"]
        params = {key: post.get(key) for key in params if post.get(key)}
        db, username, password = (
            params.get("db"),
            post.get("login"),
            post.get("password"),
        )
        _credentials_includes_in_body = all([db, username, password])
        if not _credentials_includes_in_body:
            # The request post body is empty the credetials maybe passed via the headers.
            headers = request.httprequest.headers
            db = headers.get("db")
            username = headers.get("login")
            password = headers.get("password")
            _credentials_includes_in_headers = all([db, username, password])
            if not _credentials_includes_in_headers:
                # Empty 'db' or 'username' or 'password:
                return invalid_response(
                    "missing error", "either of the following are missing [db, username,password]", 403,
                )
        # Login in odoo database:
        try:
            request.session.authenticate(db, username, password)
        except AccessError as e:
            Response.status = "401"
            return {
                "msg": "Access Error",
                "error": e
            }
        except AccessDenied:
            Response.status = "401"
            return {
                "msg": "Access Denied",
                "error": "Login, password, or db invalid."
            }
        except Exception as e:
            Response.status = "401"
            info = "The database name is not valid {}".format((e))
            error = "invalid_database"
            _logger.error(info)
            return {
                "msg": "Wrong database name.",
                "error": error
            }

        uid = request.session.uid
        # odoo login failed:
        if not uid:
            info = "Authentication Failed"
            _logger.error(info)
            Response.state = "401"
            return { "msg": info }

        # Generate tokens
        access_token = _token.find_one_or_create_token(user_id=uid, create=True)
        # Successful response:
        Response.state = "200"
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
            response=json.dumps(
                {
                    "uid": uid,
                    "user_context": request.session.get_context() if uid else {},
                    "company_id": request.env.user.company_id.id if uid else None,
                    "company_ids": request.env.user.company_ids.ids if uid else None,
                    "partner_id": request.env.user.partner_id.id,
                    "access_token": access_token,
                    "expires_in": self._expires_in,
                }
            ),
        )

    @http.route("/api/auth/token", methods=["DELETE"], type="http", auth="none", csrf=False)
    def delete(self, **post):
        """."""
        _token = request.env["api.access_token"]
        access_token = request.httprequest.headers.get("access_token")
        access_token = _token.search([("token", "=", access_token)])
        if not access_token:
            Response.state = "400"
            info = "No access token was provided in request!"
            error = "Access token is missing in the request header"
            _logger.error(info)
            return { "msg": info, "error": error }
        for token in access_token:
            token.unlink()
        # Successful response:
        return valid_response([{"desc": "access token successfully deleted", "delete": True}])
