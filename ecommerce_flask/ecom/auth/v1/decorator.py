import functools
from flask_praetorian.exceptions import MissingRoleError, InvalidTokenHeader
from ecom.auth.models import User
from ecom.extensions import guard


def roles_accepted(accepted_roles: list):
    def custom_auth_decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            token = guard.read_token_from_header()
            jwt_data = guard.extract_jwt_token(token)
            # roles_in_jwt = jwt_data.get("rls", None)
            user_id = jwt_data.get("id", None)
            user_obj = User.query.get(user_id)
            if not user_obj:
                raise InvalidTokenHeader(f"User does not exist")
            if not user_obj.is_active:
                raise InvalidTokenHeader(f"User is not active")
            if not user_obj.approved_at:
                raise InvalidTokenHeader(f"User not approved")
            roles_in_db = user_obj.role.role_name if user_obj.role else ""
            # if accepted_role.lower() != roles_in_db.lower():
            accepted_role = [role.lower() for role in accepted_roles]
            if roles_in_db.lower() not in accepted_role:
                raise MissingRoleError(
                    "This user is not having expected role to access this API"
                )
            return f(*args, **kwargs)

        return wrapper

    return custom_auth_decorator
