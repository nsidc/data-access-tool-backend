from dat_backend import app


if __name__ == "__main__":
    # `ssl_context` option:
    # https://werkzeug.palletsprojects.com/en/2.3.x/serving/#werkzeug.serving.run_simple
    app.run(host="0.0.0.0", debug=True, ssl_context="adhoc")
