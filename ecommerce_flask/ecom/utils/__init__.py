import logging, math, json, random, string, re

from typing import Union
from datetime import datetime

from werkzeug.exceptions import (
    NotFound,
    BadRequest,
    Unauthorized,
    Forbidden,
    InternalServerError,
)
from werkzeug.utils import secure_filename
from flask_restx import abort
from flask import current_app as app
from sqlalchemy import func
from email_validator import validate_email
from numerize import numerize
from wtforms import validators


class Response:
    """Generic Response class to envelope the API response."""

    @staticmethod
    def success(
        data: Union[dict, list, str] = None,
        msg=None,
        pagination: dict = None,
        links: dict = None,
        metadata: dict = None,
    ) -> dict:
        """Construct a Enveloped Success response in JSON format.
        Args:
            data (Union[dict, list, str], optional): actual data to send.\
                If None, adds `{}` to response. Defaults to None.
            pagination (dict, optional): Already constructed Pagination dictionary, \
                for List Response. If None, not added to response. Defaults to None.
            links (dict, optional): Already constructed links dictionary \
                for Paginated Response. Defaults to None.
        Returns:
            dict: Complete Enveloped success response object.
        ```py
            {
                "data": {},
                "success": true,
                "metadata":{},
                "pagination":{}
            }
        ```
        """
        _resp = {"data": data if data is not None else {}, "success": True}

        # conditionally add msg
        if msg is not None:
            _resp["message"] = msg
        else:
            if isinstance(data, str):
                _resp["message"] = data

        # conditionally add pagination
        if pagination is not None:
            _resp["pagination"] = pagination

        # conditionally add links
        # FOR FUTURE: HATEOS
        if links is not None:
            _resp["links"] = links

        # conditionally add meta_data
        if metadata is not None:
            _resp["metadata"] = metadata
        return _resp

    @staticmethod
    def failure(error_code=500, msg=None, payload=None):
        """Construct a Enveloped Failure response in JSON format
        Args:
            error_code (int, optional): Http error codes. Defaults to 500.
            msg (str, optional): Desciption of the error. Defaults to None.
            payload (Union[dict, list, str], optional): Ant extra payload with the error message. Defaults to None.
        Returns:
            dict : Enveloped Failure response in JSON
        ```py
            {
                "error": {
                    "message" : "Error"
                    "payload" : {}
                },
                "success": False
            }
        ```
        """
        if msg is None:
            msg = Response.get_default_message(error_code)
        data = {"message": msg, "payload": payload}
        return abort(error_code, None, error=data, success=False)

    @staticmethod
    def get_default_message(error_code):
        """Get the default error message if not provided.
        Args:
            error_code (int): Http error code.
        Returns:
            str: Default error message or "Error"
        """
        error_msg = {
            "400": BadRequest.description,
            "404": NotFound.description,
            "401": Unauthorized.description,
            "500": InternalServerError.description,
            "403": Forbidden.description,
        }
        return error_msg.get(str(error_code)) or "Error"
    

def check_for_string(data):
    if not isinstance(data, str):
        raise ValueError("Must be string")
    return data


def check_for_password(password_text):
    # Must be a string
    check_for_string(password_text)

    # Check if password has atleast 12 characters
    char_regex = re.compile(r"([\w\W]{12,})")
    # Check if at least one lowercase letter
    lower_regex = re.compile(r"[a-z]+")

    # Check if atleast one upper case letter
    upper_regex = re.compile(r"[A-Z]+")

    # Check if at least one digit.
    digit_regex = re.compile(r"[0-9]+")

    # Check for non-alphanumeric
    non_alpha_regex = re.compile(r"\W+")

    if char_regex.findall(password_text) == []:
        raise ValueError("Password must contain atleast 12 characters")
    elif lower_regex.findall(password_text) == []:
        raise ValueError("Password must contain atleast one lowercase character")
    elif upper_regex.findall(password_text) == []:
        raise ValueError("Password must contain atleast one uppercase character")
    elif digit_regex.findall(password_text) == []:
        raise ValueError("Password must contain atleast one digit character")
    elif non_alpha_regex.findall(password_text) == []:
        raise ValueError("Password must contain atleast one non alphanumeric character")

    return password_text


class UserAlreadyExists(Exception):
    def __str__(self):
        return "User with same mailid already exist"
    
class UserDoesNotExist(Exception):
    def __str__(self):
        return "User does not exist"