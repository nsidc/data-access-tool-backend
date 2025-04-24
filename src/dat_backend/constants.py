# TODO: is this actually helpful? It seems like we should just collapse this
# down to a dict where the key is the code and the value is the message. This is
# a legacy of hermes.
RESPONSE_CODES: dict[int, tuple[int, str]] = {
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
