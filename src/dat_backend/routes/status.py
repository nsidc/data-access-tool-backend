import datetime as dt

import flask_restx as frx
from flask import render_template
from werkzeug.wrappers import Response

from dat_backend import api
from dat_backend.constants import RESPONSE_CODES


@api.route("/api/status")
class ApplicationStatus(frx.Resource):  # type: ignore[misc]
    @api.response(*RESPONSE_CODES[200])  # type: ignore[misc]
    @api.response(*RESPONSE_CODES[500])  # type: ignore[misc]
    def get(self) -> Response:
        return Response(
            render_template(
                "application_status.html.jinja",
                request_time=dt.datetime.now(),
            ),
            content_type="text/html",
        )
