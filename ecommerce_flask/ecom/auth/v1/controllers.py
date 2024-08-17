import base64
import calendar
import logging
from datetime import datetime, timedelta

from flask import current_app as app
from flask import request, url_for
from flask_praetorian.exceptions import AuthenticationError, PraetorianError
from ecom.extensions import guard

from ecom.auth.models import User

from ecom.utils import (
    AuthExeption,
    PasswordSameException,
    Response,
    generate_password,
)


def get_access_token(username, password):
    try:
        user = guard.authenticate(username, password)
        access_token = guard.encode_jwt_token(user)
        return {"access_token": access_token}
    except AuthExeption as ae:
        return Response.failure(ae.err_code, ae.msg, ae.payload)
    except Exception as exc:
        logging.error(str(exc))
        return Response.failure(500, payload=str(exc))
    

def get_refresh_token_from_old_access_token():
    """Generate a new JWT token from the old token if it is expired

    Returns:
        [token]: JWT refresh token
    """
    token = guard.read_token_from_header()
    token_response = {"access_token": guard.refresh_jwt_token(token)}
    return token_response


def get_user_info():
    """Get user information from DB.

    Extract user id from jwt token to get user information.

    Returns:
        dict: user information
    """
    token = guard.read_token_from_header()
    user_id = guard.extract_jwt_token(token)["id"]
    user = User.identify(user_id)
    if user:
        return Response.success(user)
    return Response.failure(400, "Unable to identify the user")


def verify_old_password_and_update_password(username, old_password, new_password):
    try:
        user = guard.authenticate(username, old_password)
        if user.password_changed_at is not None:
            password_changed_days = datetime.utcnow() - user.password_changed_at
            if (
                password_changed_days.days
                <= app.config["PASSWORD_CHANGE_REQUIRED_DAYS"]
            ):
                raise AuthExeption(
                    msg="ExpiredPasswordError",
                    payload=f"Your password is changed recently, You need to wait for {password_changed_days.days} days to change your password",
                )
    except AuthExeption as ae:
        return Response.failure(ae.err_code, ae.msg, ae.payload)
    except Exception as exc:
        logging.error(str(exc))
        return Response.failure(500, payload=str(exc))
    
    User.update_user(user.user_id, password=new_password)
    return Response.success("Password Updated Successfully")

