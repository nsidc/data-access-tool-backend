import os
import logging
import re
import traceback

import flask_restx as frx
from flask import Flask, render_template
from flask_cors import CORS
from flask_caching import Cache
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response

from dat_backend.reverse_proxy import ReverseProxied
from dat_backend.constants import RESPONSE_CODES

__version__ = "1.1.0"


app = Flask(__name__)
# Enable CORS, allowing all nsidc.org domains.
CORS(
    app,
    origins=[re.compile(r"^https?:\/\/(.*\.)?nsidc\.org")],
    expose_headers=["content-disposition"],
    supports_credentials=True,
)
api = frx.Api(
    app,
    version=__version__,
    title="Data Access Tool API",
    description="Backend services for the Data Access Tool.",
)

app.wsgi_app = ReverseProxied(app.wsgi_app)  # type: ignore[method-assign]

app.logger.setLevel(logging.INFO)

secret_key = os.environ.get("DAT_FLASK_SECRET_KEY")
app.secret_key = secret_key

# Setup caching
cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 60})
cache.init_app(app)

# Required for the error handler below to work correctly. Without this set, the
# flask-restx error handler takes primary responsibiliy for handling the
# error. Although there is a way to register a flask-restx error handler with
# `@api.errorhandler`, there are limits on its capabilities:
# https://github.com/python-restx/flask-restx/issues/458
# https://flask.palletsprojects.com/en/stable/config/#PROPAGATE_EXCEPTIONS
app.config.update({"PROPAGATE_EXCEPTIONS": True})


@app.errorhandler(Exception)  # noqa
def handle_exception(e):
    """Handle any exceptions raised from the application.

    https://flask.palletsprojects.com/en/stable/errorhandling/#error-handlers
    """
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e
    # Log the error
    err_traceback = traceback.format_exception(e)
    err_msg = f"Unhandled exception during request: {e}"
    app.logger.exception(err_msg, extra={"exception_traceback": err_traceback})

    # Return a 500 response
    return Response(
        render_template(
            "generic_error.html.jinja",
            status_code=RESPONSE_CODES[500][0],
            status_message=RESPONSE_CODES[500][1],
        ),
        content_type="text/html",
        status=RESPONSE_CODES[500][0],
    )


# Imports of modules containing routes come after . This is necessary so that all of the
# APIs are defined when this file is done initializing.
from dat_backend.routes.earthdata_download import auth, get_links  # noqa
from dat_backend.routes import status, python_script, metrics, favicon  # noqa
