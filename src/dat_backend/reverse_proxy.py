from typing import Iterable, TYPE_CHECKING

# https://git.io/fhHMJ
if TYPE_CHECKING:
    from wsgiref.types import StartResponse, WSGIApplication, WSGIEnvironment


class ReverseProxied(object):
    """Adapted from Flask Snippets.

        https://web.archive.org/web/20190523102024/http://flask.pocoo.org/snippets/35/

    Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    """

    def __init__(self, app: "WSGIApplication"):
        self.app = app
        self.api_root = "/"

    def __call__(
        self, environ: "WSGIEnvironment", start_response: "StartResponse"
    ) -> Iterable[bytes]:
        script_name = environ.get("HTTP_X_SCRIPT_NAME", "")
        if script_name:
            self.api_root = script_name
            environ["SCRIPT_NAME"] = script_name
            path_info = environ["PATH_INFO"]
            if path_info.startswith(script_name):
                environ["PATH_INFO"] = path_info[len(script_name) :]

        scheme = environ.get("HTTP_X_FORWARDED_PROTO", "")
        if scheme:
            environ["wsgi.url_scheme"] = scheme

        server = environ.get("HTTP_X_FORWARDED_HOST", "")
        if server:
            environ["HTTP_HOST"] = server

        return self.app(environ, start_response)
