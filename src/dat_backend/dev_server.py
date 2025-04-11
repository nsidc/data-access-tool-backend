import logging

from dat_backend import app


if __name__ == "__main__":
    # Setup file handler for dev server (this is handled by gunicorn in non-dev
    # environments)
    filehandler = logging.FileHandler("/tmp/logs/error.log")
    filehandler.setLevel(logging.INFO)
    app.logger.addHandler(filehandler)

    # Set to debug log level
    app.logger.setLevel(logging.DEBUG)

    # Run the flask app
    app.run(
        host="0.0.0.0",
        debug=True,
        # https://werkzeug.palletsprojects.com/en/2.3.x/serving/#werkzeug.serving.run_simple
        ssl_context="adhoc",
    )
