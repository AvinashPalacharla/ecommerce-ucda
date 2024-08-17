import json
import logging
from re import L
import uuid
import pandas as pd
from flask import current_app as app
from io import BytesIO

import pandas as pd

from sqlalchemy import table, func

from ecom.constants import (
    ROLES_SEED_DATA,
    USERS_SEED_DATA,
)

from ecom.auth.models import Role, User
from ecom.extensions import  db



def create_roles():
    """Method used to create initial set of roles for the application."""
    logging.info("Attempting to create Roles")
    # manually deleting Client Admin as this role is not required
    Role.query.filter_by(role_name="Client Admin").delete()
    # manually updating Business user as spelling was wrong
    db.session.query(Role).filter_by(role_name="Buisness User").update(
        {"role_name": "Business User", "description": "Role for business users"}
    )
    for _role in ROLES_SEED_DATA:
        if not Role.lookup(str(_role["role_name"])):
            Role.create_role(
                role_name=str(_role["role_name"]),
                description=_role["role_desc"],
            )
    db.session.commit()
    logging.info("Roles creation finished")


def create_users():
    """Method used to create initial/dummy users for the application."""
    logging.info("Attempting to create Users")
    for user in USERS_SEED_DATA:
        looked_up_user = User.lookup(user["email"])
        if not looked_up_user:
            User.create_user(
                first_name=user["first_name"],
                last_name=user["last_name"],
                email=user["email"],
                password=app.config["DEFAULT_PASSWORD"],
                role=user["role"],
            )
        else:
            User.update_user(
                looked_up_user.user_id,
                first_name=user["first_name"],
                last_name=user["last_name"],
                password=app.config["DEFAULT_PASSWORD"],
                role=user["role"],
            )
    logging.info("Users creation finished")


def flask_profiler():
    table_exists_query = """IF EXISTS (
        SELECT * FROM information_schema.tables
        WHERE table_name = 'flask_profiler_measurements'
        )  SELECT 1 AS res ELSE SELECT 0 AS res;
    """
    table_exists_qset = db.engine.execute(table_exists_query)
    table_exists = 0
    # print(f"Table Exists: {table_exists.__dict__}")
    for cursor in table_exists_qset:
        # print(f"Table exists: {cursor[0]}")
        table_exists = cursor[0]

    if table_exists == 0:
        logging.info(f"Creating flask_profiler table.... ")
        db.engine.execute(
            """
            CREATE TABLE [flask_profiler_measurements] (
            id [int] IDENTITY(1,1) NOT NULL,
            startedAt float DEFAULT NULL,
            endedAt float DEFAULT NULL,
            elapsed float DEFAULT NULL,
            method text,
            args text,
            kwargs text,
            name text,
            context text,
            PRIMARY KEY (id)
            );
        """
        )