from functools import wraps
from flask import request
from werkzeug.exceptions import (
    BadRequest,
    Unauthorized,
    Forbidden,
    InternalServerError,
)
from flask import current_app as app


def _valid_token(current_token):
    _token_list = [
        "e)>N0pf,2X4(&0huO2l&^JUugYzyFCKComzhcFig3Hmraailg42af8$/_FWL<~QItOPZM",
        "G3FWxYT0oBaIu]C=XK^:6A-.+X7|rDi=y;^)/n6>QZYt428$[z</_FW~hOixr1nlRgPjG",
    ]
    if current_token in _token_list:
        return True
    else:
        return False


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # take token out of header
        token = None
        if "X-API-KEY" in request.headers:
            token = request.headers["X-API-KEY"]

        # check if token available
        if not token:
            raise Unauthorized

        # check if token correct
        if not _valid_token(token):
            raise Unauthorized

        # call original function f() now haves access to g.user
        return f(*args, **kwargs)

    return wrapper
