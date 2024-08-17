import logging
from flask.cli import AppGroup, with_appcontext
from flask import current_app as app
from os import getenv

from ecom.commands_seed_data import (
    create_roles,
    create_users,
    flask_profiler
)
from ecom.extensions import db, cache


ecom_cli = AppGroup("ecom", help="ECOM custom CLI commands")


@ecom_cli.command(name="create_roles")
@with_appcontext
def create_roles_command():
    """create_roles command used to create initial/dummy users for the application."""
    create_roles()



@ecom_cli.command(name="create_users")
@with_appcontext
def create_users_command():
    """create_users command used to create initial/dummy users for the application."""
    create_users()


@ecom_cli.command(name="deploy")
@with_appcontext
def deploy():
    logging.root.setLevel(logging.NOTSET)
    logger = logging.getLogger("seed")

    logger.info("Running Flask Deployment Script")

    logger.info("Started Creating Roles")
    create_roles()
    logger.info("Completed Creating Roles")

    logger.info("Started Creating Users")
    create_users()
    logger.info("Completed Creating Users")

    if app.config["RUN_PROFILER"] is True:
        flask_profiler()

    try:
        cache.clear()  # To clear the cache while deploying the app
    except Exception as exc:
        logging.error(
            "Failed to clear cache. This happends mostly when connection to Redis could not be established. Exception: %s"
            % (str(exc))
        )

    return


