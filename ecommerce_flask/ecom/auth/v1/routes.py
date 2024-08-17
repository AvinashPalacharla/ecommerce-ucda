from flask_restx import Namespace, Resource, reqparse
import flask_praetorian

from ecom.utils import check_for_password
from . import controllers

api = Namespace("Auth", description="Auth related routes")

@api.route("/login")
class Login(Resource):
    """class for user login functions"""

    @flask_praetorian.auth_required
    def get(self):
        """get current user name

        Returns:
            [str]: current user username
        """
        return {"username": flask_praetorian.current_user().username}

    def post(self):
        """
        Logs a user in by parsing a POST request containing user credentials and
        issuing a JWT token for guest user.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True, nullable=False)
        parser.add_argument("password", type=str, required=True, nullable=False)
        args = parser.parse_args()
        return controllers.get_access_token(args["username"], args["password"])
    

@api.route("/refresh-token")
class RefreshToken(Resource):
    """class for refresh JWT token functions"""

    def get(self):
        """Get new JWT token from the old one only if it is expired

        Returns:
            [token]: JWT refresh token
        """
        return controllers.get_refresh_token_from_old_access_token()
    

@api.route("/identity")
class UserInfo(Resource):
    def get(self):
        """Get user information from token"""
        return controllers.get_user_info()
    

@api.route("/change-password")
class ChangePassword(Resource):
    def put(self):
        """ """
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True, nullable=False)
        parser.add_argument(
            "old_password",
            type=check_for_password,
            location="json",
            required=True,
            nullable=False,
        )
        parser.add_argument(
            "new_password",
            type=check_for_password,
            location="json",
            required=True,
            nullable=False,
        )
        args = parser.parse_args()

        return controllers.verify_old_password_and_update_password(args["username"], args["old_password"], args["new_password"])