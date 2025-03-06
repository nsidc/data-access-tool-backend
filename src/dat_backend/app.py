import base64
import datetime as dt
import io
import os
import pprint
from typing import Any, Final, Optional, Dict
import logging

import requests
import flask_restx as frx
from flask import (
    make_response,
    send_file,
    request,
    url_for,
    redirect,
    session,
    render_template,
)
from flask import Flask
import pydantic
from werkzeug.wrappers import Response

from dat_backend.get_links import get_links


app = Flask(__name__)
api = frx.Api(app)

app.logger.setLevel(logging.INFO)

# TODO: regenerate and move into secrets storage.
secret_key = "87b8af58ade1d827860a52c25c55b0f75c8286195c62531a4cdc4bd152fe6116"
app.secret_key = secret_key

RESPONSE_CODES = {
    200: (200, "Success"),
    201: (201, "Created"),
    302: (302, "Found"),
    303: (303, "See Other"),
    400: (400, "Validation error"),
    401: (401, "Unauthorized"),
    403: (403, "Forbidden"),
    404: (404, "Not found"),
    409: (409, "Conflict"),
    500: (500, "Internal server error"),
}


class SelectionFilters(pydantic.BaseModel):
    bounding_box: str
    dataset_short_name: str
    dataset_version: str
    time_start: dt.datetime
    time_end: dt.datetime
    polygon: str
    filename_filter: str


def cmr_datetime_format(dt: dt.datetime) -> str:
    """CMR only supports the 'Z' ISO 8601 suffix.

    Replace the default datetime.isoformat() suffix ('+00:00') with 'Z'.
    """
    return dt.isoformat().replace("+00:00", "Z")


SCRIPT_DOC: Final[frx.model.Model] = api.model(
    "Script",
    {
        "bounding_box": frx.fields.String(
            description="the bounding box", example="-180,-90,180,90", required=False
        ),
        "dataset_short_name": frx.fields.String(
            description="the collection ID", example="MOD10A2", required=True
        ),
        "dataset_version": frx.fields.String(
            description="the collection version", example="6", required=True
        ),
        "time_start": frx.fields.String(
            description="the start datetime (UTC) filter",
            example="1999-12-18T00:00:00Z",
            required=False,
        ),
        "time_end": frx.fields.String(
            description="the end datetime (UTC) filter",
            example="2019-03-07T22:09:38Z",
            required=False,
        ),
        "polygon": frx.fields.String(
            description="the polygon filter",
            example="-109,37,-102,37,-102,41,-109,41,-109,37",
            required=False,
        ),
        "filename_filter": frx.fields.String(
            description="the filename filter", example="*2019*", required=False
        ),
    },
)


@api.route("/api/downloader-script/")
class DataDownloaderScript(frx.Resource):  # type: ignore[misc]

    @api.response(200, "Success")  # type: ignore[misc]
    @api.expect(SCRIPT_DOC)  # type: ignore[misc]
    def post(self) -> Any:
        current_date = dt.date.today().isoformat()

        url_list = api.payload.get("url_list")
        if url_list:
            script_parameters = {
                "{short_name}": "",
                "{version}": "",
                "{time_start}": "",
                "{time_end}": "",
                "{bounding_box}": "",
                "{polygon}": "",
                "{filename_filter}": "",
                "'{url_list}'": pprint.pformat(url_list),
            }
            app.logger.info(
                f"Script request received successfully: {len(url_list)} URLs"
            )
            filename = f"nsidc-download_{current_date}.py"

        else:
            try:
                selection_filters = SelectionFilters(**api.payload)
                app.logger.info(
                    f"Script request received successfully: {selection_filters}"
                )
            # This validation error should come from pydantic.
            except pydantic.ValidationError as e:
                app.logger.exception(e)
                frx.abort(400, f"Validation failed. {e}")
            except RuntimeError as e:
                app.logger.exception(e)
                frx.abort(400, str(e))

            script_parameters = {
                "{short_name}": selection_filters.dataset_short_name,
                "{version}": selection_filters.dataset_version,
                "{time_start}": cmr_datetime_format(selection_filters.time_start),
                "{time_end}": cmr_datetime_format(selection_filters.time_end),
                "{bounding_box}": selection_filters.bounding_box,
                "{polygon}": selection_filters.polygon,
                "{filename_filter}": selection_filters.filename_filter,
                "'{url_list}'": "[]",
            }

            version = selection_filters.dataset_version.zfill(3)
            filename = f"nsidc-download_{selection_filters.dataset_short_name}.{version}_{current_date}.py"

        app.logger.info("Building script...")

        fp = os.path.join(os.path.dirname(__file__), "templates", "python_script.py")
        with open(fp, "r") as file:
            script = file.read()

        script_parameters["{copyright_year}"] = str(dt.date.today().year)

        # Do not use .format, otherwise we can't have {} within the python_script file.
        for param, value in script_parameters.items():
            script = script.replace(param, value)

        stream = io.BytesIO()
        stream.write(script.encode("utf-8"))
        stream.seek(0)

        response = make_response(
            send_file(
                stream,
                mimetype="application/x-python",
                as_attachment=True,
                download_name=filename,
            )
        )

        return response


# TODO: re-add this and make use of it. This gives the swagger interface more
# information and helps to document the API.
# GET_LINKS_DOC: Final[frx.model.Model] = api.model(
#     "get_links",
#     {
#         "cmr_request_params": frx.fields.String(
#             description="CMR Request parameters as a string",
#             example="provider=NSIDC_ECS&page_size=2000&sort_key[]=-start_date&sort_key[]=producer_granule_id&short_name=ATL06&version=6&version=06&version=006&temporal[]=2018-10-14T00:00:00Z,2025-02-19T20:51:37Z&bounding_box=-101.94,57.71,-90.21,61.13",
#             required=True,
#         ),
#         "cursor": frx.fields.String(
#             description="CMR search results cursor",
#             example='1638327816913,"atl06_20211201030329_10641303_006_01.h5",2706594203',
#             required=False,
#         ),
#     },
# )


@api.route("/api/get-links")
class GetLinks(frx.Resource):  # type: ignore[misc]

    @api.response(200, "Success")
    # @api.expect(GET_LINKS_DOC)  # type: ignore
    def get(self):
        # cmr_request_params = api.payload["cmr_request_params"]
        cmr_request_params = request.args.get("cmr_request_params")
        cursor = request.args.get("cursor")
        # cursor = api.payload.get("cursor")
        app.logger.info(
            f"get_links received successfully: {cmr_request_params=} {cursor=}"
        )

        # TODO: remove hard-coded params. We may need to break these out into
        # individual args instead of just passing a query string...encoding this
        # in a way that the earthdata downloader can pass the requests along is
        # difficult. Not sure how to achieve yet.
        cmr_request_params = "provider=NSIDC_CPRD&page_size=5&sort_key[]=-start_date&sort_key[]=producer_granule_id&short_name=ATL06&version=6&version=06&version=006&temporal[]=2018-10-14T00:00:00Z,2025-02-25T00:25:20Z&bounding_box=-180,-90,180,90&options[producer_granule_id][pattern]=true&producer_granule_id[]=*ATL06_2024*_0804*_006_01.h5*"

        app.logger.info(f"get_links using {cursor=}")
        links, cursor = get_links(
            cmr_request_params=cmr_request_params,
            search_after_cursor=cursor,
        )
        app.logger.info(f"get_links found new {cursor=}")

        orders_done = len(links) == 0
        if not orders_done:
            app.logger.info(f"first link: {links[0]}")
        response = {
            "links": links,
            "done": orders_done,
            "cursor": cursor,
        }

        return response


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


@api.route("/api/earthdata/auth/")
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
        edl_auth_finish_redirect_uri = url_for("earthdata_auth_finish", _external=True)
        app.logger.info(f"Using {edl_auth_finish_redirect_uri=}")
        earthdata_authorize_url += "&redirect_uri={0}".format(
            edl_auth_finish_redirect_uri
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
    redirect_uri = url_for("earthdata_auth_finish", _external=True)

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
        raise Exception("Authorization Failed")

    authorization_result_json: Dict[str, Any] = authorization_result.json()

    app.logger.info("result json: {0}".format(authorization_result_json))

    return authorization_result_json


# TODO: Consider renaming to `/login_callback/` or `/auth_callback/`
@api.route("/api/earthdata/auth_finish/")
class EarthdataAuthFinish(frx.Resource):  # type: ignore[misc]
    @api.response(*RESPONSE_CODES[302])  # type: ignore[misc]
    @api.response(*RESPONSE_CODES[500])  # type: ignore[misc]
    def get(self) -> Response:
        # Perform token exchange
        authorization_code: Optional[str] = request.args.get("code")
        earthdata_auth_result = earthdata_token_exchange(authorization_code)
        user_edl_token = earthdata_auth_result["access_token"]

        app.logger.info("Authorized with token: {0}".format(user_edl_token))

        eddRedirect = session.pop("eddRedirect")
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


@api.route("/api/test/")
class EarthdataAuthFinish(frx.Resource):  # type: ignore[misc]
    @api.response(*RESPONSE_CODES[302])  # type: ignore[misc]
    @api.response(*RESPONSE_CODES[500])  # type: ignore[misc]
    def get(self) -> Response:
        return "Hello, world!"


if __name__ == "__main__":
    # `ssl_context` option:
    # https://werkzeug.palletsprojects.com/en/2.3.x/serving/#werkzeug.serving.run_simple
    app.run(host="0.0.0.0", debug=True, ssl_context="adhoc")
