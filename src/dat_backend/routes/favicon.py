from pathlib import Path

import flask_restx as frx
from flask import send_from_directory
from werkzeug.wrappers import Response

from dat_backend import api
from dat_backend.constants import RESPONSE_CODES


@api.route("/favicon.ico")
class Favicon(frx.Resource):  # type: ignore[misc]
    @api.response(*RESPONSE_CODES[200])  # type: ignore[misc]
    @api.response(*RESPONSE_CODES[500])  # type: ignore[misc]
    def get(self) -> Response:
        # https://flask.palletsprojects.com/en/stable/patterns/favicon/
        return send_from_directory(
            str(Path(__file__).parent / ".." / "static"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )
