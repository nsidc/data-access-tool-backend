import os
import logging
import re

import flask_restx as frx
from flask import Flask
from flask_cors import CORS

from dat_backend.reverse_proxy import ReverseProxied


app = Flask(__name__)
# Enable CORS, allowing all nsidc.org domains.
CORS(
    app,
    origins=[re.compile(r"^https?:\/\/(.*\.)?nsidc\.org")],
    expose_headers=["content-disposition"],
    supports_credentials=True,
)
api = frx.Api(app)

app.wsgi_app = ReverseProxied(app.wsgi_app)  # type: ignore[method-assign]

app.logger.setLevel(logging.INFO)

secret_key = os.environ.get("DAT_FLASK_SECRET_KEY")
app.secret_key = secret_key


# Imports of modules containing routes come after . This is necessary so that all of the
# APIs are defined when this file is done initializing.
from dat_backend.routes.earthdata_download import auth, get_links  # noqa
from dat_backend.routes import status, python_script  # noqa

if __name__ == "__main__":
    # `ssl_context` option:
    # https://werkzeug.palletsprojects.com/en/2.3.x/serving/#werkzeug.serving.run_simple
    app.run(host="0.0.0.0", debug=True, ssl_context="adhoc")
