import base64
import calendar
import logging
from datetime import datetime, timedelta

from flask import current_app as app
from flask import request, url_for
from flask_praetorian.exceptions import AuthenticationError, PraetorianError
from ecom.extensions import guard
from itsdangerous import TimedSerializer as Serializer, BadSignature, SignatureExpired
from flask_mail import Message
import random
import datetime
from ecom.auth.models import User, OTP
from ecom.extensions import db, mail

from ecom.utils import (
    AuthExeption,
    PasswordSameException,
    Response,
    generate_password,
)


def get_serializer():
    """Create a Serializer instance with the app context."""
    return Serializer(app.config["SECRET_KEY"])

def generate_token(email):
    s = get_serializer()
    return s.dumps({'email': email})

def verify_token(token):
    s = get_serializer()
    try:
        data = s.loads(token)
        return data['email']
    except (BadSignature, SignatureExpired):
        return None

def send_reset_email(email, token):
    reset_url = url_for('api.reset_password', token=token, _external=True)
    msg = Message('Password Reset Request', recipients=[email])
    msg.body = f'Please use the following link to reset your password: {reset_url}'
    mail.send(msg)



def forgot_password(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return Response.failure(404, 'No account found with that email address')

    token = generate_token(email)
    print(token)
    send_reset_email(email, token)
    return Response.success(200, "Password reset email sent")


def reset_password(token):
    email = verify_token(token)
    if not email:
        return Response.failure(400, 'Invalid or expired token')

    new_password = request.json.get('new_password')
    if not new_password:
        return Response.failure(400, 'New password is required')

    user = User.query.filter_by(email=email).first()
    if not user:
        return Response.failure(404, 'User not found')

    User.update_user(user.user_id, password=new_password)

    return Response.success(200, 'Password updated successfully')


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
            password_changed_days = datetime.datetime.utcnow() - user.password_changed_at
            required_days = app.config["PASSWORD_CHANGE_REQUIRED_DAYS"]
            print(password_changed_days)
            if (
                password_changed_days.days
                <= required_days
            ):
                raise AuthExeption(
                    msg="ExpiredPasswordError",
                    payload=f"Your password is changed recently, You need to wait for {required_days-password_changed_days.days} days to change your password",
                )
    except AuthExeption as ae:
        return Response.failure(ae.err_code, ae.msg, ae.payload)
    except Exception as exc:
        logging.error(str(exc))
        return Response.failure(500, payload=str(exc))
    
    User.update_user(user.user_id, password=new_password)
    return Response.success("Password Updated Successfully")

