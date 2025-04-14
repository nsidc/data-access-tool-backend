import os
import logging
import re
import traceback

import flask_restx as frx
from flask import Flask
from flask_cors import CORS
from flask_caching import Cache

from dat_backend.reverse_proxy import ReverseProxied
from dat_backend.constants import RESPONSE_CODES

__version__ = "0.5.0"


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


@app.errorhandler(Exception)  # noqa
def handle_exception(e):
    """Handle any exceptions raised from the application.

    https://flask.palletsprojects.com/en/stable/errorhandling/#error-handlers
    """
    # Log the error
    err_traceback = traceback.format_exception(e)
    err_msg = f"Unhandled exception during request: {e}"
    app.logger.exception(err_msg, extra={"exception_traceback": err_traceback})

    # Return a 500 response
    response_code, response_message = RESPONSE_CODES[500]
    return response_message, response_code


# Imports of modules containing routes come after . This is necessary so that all of the
# APIs are defined when this file is done initializing.
from dat_backend.routes.earthdata_download import auth, get_links  # noqa
from dat_backend.routes import status, python_script, metrics  # noqa

if __name__ == "__main__":
    # `ssl_context` option:
    # https://werkzeug.palletsprojects.com/en/2.3.x/serving/#werkzeug.serving.run_simple
    app.run(host="0.0.0.0", debug=True, ssl_context="adhoc")
