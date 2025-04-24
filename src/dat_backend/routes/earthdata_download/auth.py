import base64
import os
from typing import Any, Optional, Dict

import requests
import flask_restx as frx
from flask import (
    request,
    url_for,
    redirect,
    session,
    render_template,
)
from werkzeug.wrappers import Response

from dat_backend import api, app
from dat_backend.constants import RESPONSE_CODES

# Auth code copied and adapted from `hermes-api`
# See: https://urs.earthdata.nasa.gov/documentation/for_integrators/edl_integration
uat = False
if uat:
    EARTHDATA_APP_CLIENT_ID = os.environ.get("EARTHDATA_UAT_APP_CLIENT_ID")
    EARTHDATA_APP_UID = os.environ.get("EARTHDATA_UAT_APP_USERNAME")
    EARTHDATA_APP_PASSWORD = os.environ.get("EARTHDATA_UAT_APP_PASSWORD")

else:
    EARTHDATA_APP_CLIENT_ID = os.environ.get("EARTHDATA_APP_CLIENT_ID")
    EARTHDATA_APP_UID = os.environ.get("EARTHDATA_APP_USERNAME")
    EARTHDATA_APP_PASSWORD = os.environ.get("EARTHDATA_APP_PASSWORD")


@api.route("/api/earthdata/auth")
class EarthdataAuth(frx.Resource):  # type: ignore[misc]
    @api.response(*RESPONSE_CODES[302])  # type: ignore[misc]
    @api.response(*RESPONSE_CODES[500])  # type: ignore[misc]
    def get(self) -> Response:
        app.logger.info("AUTH HAPPENING HERE!")
        app.logger.info(f"Got {request.args}")
        eddRedirect = request.args.get("eddRedirect")
        referrer = request.referrer

        app.logger.info(f"Received {eddRedirect=}")
        session["referrer"] = referrer
        session["eddRedirect"] = eddRedirect

        earthdata_authorize_url = "https://urs.earthdata.nasa.gov/oauth/authorize"
        earthdata_authorize_url += "?client_id={0}".format(EARTHDATA_APP_CLIENT_ID)
        earthdata_authorize_url += "&response_type=code"
        edl_auth_callback_redirect_uri = url_for(
            "earthdata_auth_callback",
            _external=True,
        )
        app.logger.info(f"Using {edl_auth_callback_redirect_uri=}")
        earthdata_authorize_url += "&redirect_uri={0}".format(
            edl_auth_callback_redirect_uri
        )

        response = redirect(earthdata_authorize_url, code=302)
        return response


def earthdata_token_exchange(authorization_code: Optional[str]) -> Dict[str, Any]:
    # Example response:
    #   {
    #     u'access_token': u'secret',  # noqa
    #     u'token_type': u'Bearer',
    #     u'endpoint': u'/api/users/kbeam',
    #     u'expires_in': 3600,
    #     u'refresh_token': u'secret'  # noqa
    #   }

    # TODO: This URL maybe needs to be parametrized like in Constants.py
    earthdata_token_api = "https://urs.earthdata.nasa.gov/oauth/token"
    grant_type = "authorization_code"
    redirect_uri = url_for("earthdata_auth_callback", _external=True)

    credentials = f"{EARTHDATA_APP_UID}:{EARTHDATA_APP_PASSWORD}"
    auth = base64.b64encode(credentials.encode("ascii")).decode("ascii")

    headers = {"Authorization": "BASIC {0}".format(auth)}

    authorization_data = {
        "grant_type": grant_type,
        "code": authorization_code,
        "redirect_uri": redirect_uri,
    }

    authorization_result = requests.post(
        earthdata_token_api, headers=headers, data=authorization_data
    )

    if authorization_result.status_code != 200:
        raise Exception(f"Authorization Failed: {authorization_result.text}")

    authorization_result_json: Dict[str, Any] = authorization_result.json()

    app.logger.info("result json: {0}".format(authorization_result_json))

    return authorization_result_json


@api.route("/api/earthdata/auth_callback")
class EarthdataAuthCallback(frx.Resource):  # type: ignore[misc]
    @api.response(*RESPONSE_CODES[200])  # type: ignore[misc]
    @api.response(*RESPONSE_CODES[500])  # type: ignore[misc]
    def get(self) -> Response:
        # Perform token exchange
        authorization_code: Optional[str] = request.args.get("code")
        earthdata_auth_result = earthdata_token_exchange(authorization_code)
        user_edl_token = earthdata_auth_result["access_token"]

        app.logger.info("Authorized with token: {0}".format(user_edl_token))

        eddRedirect = session.get("eddRedirect")
        if not eddRedirect:
            # The client likely does not support cookies, which means that Flask
            # cannot associate the current request with the appropriate session
            # containing the eddRedirect.
            # Return 400, bad request, with a handy error message
            return Response(
                render_template(
                    "edd_auth_session_fail.html.jinja",
                    status_code=RESPONSE_CODES[400][0],
                    status_message=RESPONSE_CODES[400][1],
                ),
                content_type="text/html",
                status=RESPONSE_CODES[400][0],
            )

        # Redirect back to the application
        # The eddRedirect includes the `FileId` query parameter already set and
        # will look something like this:
        # `earthdata-download://authCallback?fileId=6833`
        # Add the user's access token:
        auth_callback_deeplink = f"{eddRedirect}&token={user_edl_token}"
        app.logger.info(f"Using auth callback redirect: {auth_callback_deeplink}")

        # TODO: using a redirect here does not work, because the protocol+host
        # bit of the redirect URI gets cast to lowercase. EDD expects
        # `earthdata-download://authCallback`, but using `redirect` always
        # results in the `Location` header showing
        # `earthdata-download://authcallback` (lowercase `c` in
        # `callback`). This is NOT recognized by the EDD. The correct casing
        # must be maintained.
        # response = redirect(
        #     auth_callback_deeplink,
        # )
        # This response returns an html page with a script that opens the
        # deeplink and then closes the associated windows.
        return Response(
            render_template(
                "edd_auth_callback.html.jinja",
                redirect_uri=auth_callback_deeplink,
            ),
            content_type="text/html",
        )
