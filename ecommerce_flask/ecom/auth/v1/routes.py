from flask_restx import Namespace, Resource, reqparse
import flask_praetorian

from ecom.utils import check_for_password
from . import controllers

api = Namespace("Auth", description="Auth related routes")

