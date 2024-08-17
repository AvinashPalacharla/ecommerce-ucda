"""Environment Specific Config Values should be set here
    """

import json
import os
from urllib.parse import quote_plus as urlquote

from ecom.extensions import get_redis_cache
from urllib.parse import quote_plus

BASE_DIR = os.path.abspath(os.path.dirname(__name__))
TRUTHY_VALUES = ["True", True, "true", "1", 1, "yes", "Yes", "Y", "y"]


class BaseConfig(object):
    # Flask variables
    DEBUG = False
    TESTING = False
    BUNDLE_ERRORS = os.getenv("BUNDLE_ERRORS", "False") in TRUTHY_VALUES
    TRUTHY_VALUES = TRUTHY_VALUES

    # To safely convert datetime objects while sending response back to frontend
    RESTX_JSON = {"default": str}
    # for flask restx abort
    ERROR_INCLUDE_MESSAGE = False
    SECRET_KEY = os.getenv("APP_VALIDATION_KEY") or os.urandom(15).hex()

    # sql db specific
    APP_DB_USER = os.getenv("APP_DB_USER")
    APP_DB_SECRET = os.getenv("APP_DB_SECRET")
    APP_DB_HOST = os.getenv("APP_DB_HOST")
    APP_DB_PORT = os.getenv("APP_DB_PORT")
    APP_DB_NAME = os.getenv("APP_DB_NAME")

    BASIC_AUTH_USERNAME = os.getenv("ADMIN_USERNAME")
    BASIC_AUTH_PASSWORD = os.getenv("ADMIN_PASSWORD")

    """ if APP_DB_USE_SSL:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {
                "ssl": {
                    "sslmode": "require",
                    # "sslrootcert": "/etc/ssl/certs/mysql.crt.pem",
                    "sslrootcert": "mysql.crt.pem",
                },
            }
        } """
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{APP_DB_USER}:{quote_plus(APP_DB_SECRET)}@{APP_DB_HOST}:{APP_DB_PORT}/{APP_DB_NAME}"

    # to disable logs of sqlalchemy
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # flask-caching variables
    CACHE_TYPE = os.getenv("CACHE_TYPE", "null")
    CACHE_REDIS_HOST = os.getenv("CACHE_HOST")
    CACHE_REDIS_PORT = os.getenv("CACHE_PORT")
    CACHE_REDIS_DB = os.getenv("CACHE_DB")
    CACHE_REDIS_PASSWORD = os.getenv("CACHE_SECRET")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", "120"))

    DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "Dummy@1234567")

    # flask-praetorian variables
    JWT_ACCESS_LIFESPAN = {"minutes": int(os.environ.get("ACCESS_TOKEN_EXPIRY_MINS"))}
    JWT_REFRESH_LIFESPAN = {"minutes": int(os.environ.get("REFRESH_TOKEN_EXPIRY_MINS"))}

    # JWT token related (Not related to flask-praetorian, this is custom)
    JWT_REGISTRATION_LIFESPAN = (
        f"""{int(os.environ.get("REGISTRATION_TOKEN_EXPIRY_DAYS", 30))} days"""
    )
    JWT_RESET_LIFESPAN = (
        f"""{int(os.environ.get("PASSWORD_RESET_TOKEN_EXPIRY_MINS", 5))} mins"""
    )

    REFRESH_DATA_TOKEN = os.getenv("REFRESH_DATA_TOKEN", "")

    BASIC_AUTH_USERNAME = os.getenv("ADMIN_USERNAME")
    BASIC_AUTH_PASSWORD = os.getenv("ADMIN_PASSWORD")

    RUN_PROFILER = os.getenv("RUN_PROFILER", False) in TRUTHY_VALUES

    # Authentication realted
    # It is also configured in constants.py file
    # If there are any changes, reflect the same there as well
    AUTH_CODE_EXPIRY_INTERVAL = {
        "auth_app": int(os.environ.get("AUTH_CODE_EXPIRY_INTERVAL_AUTH_APP", 30)),
        "mail": int(os.environ.get("AUTH_CODE_EXPIRY_INTERVAL_MAIL", 120)),
    }
    SKIP_SEED_USERS_AUTH_CHECKS = (
        os.getenv("SKIP_SEED_USERS_AUTH_CHECKS", "false") in TRUTHY_VALUES
    )

    REDIS_URL = os.getenv("broker_url")


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False

    # Database Related - Connect to local sqlite in dev if not specified otherwise in .env
    # SQLALCHEMY_DATABASE_URI = os.getenv(
    #     "SQLALCHEMY_DATABASE_URI"
    # ) or "sqlite:///" + os.path.join(BASE_DIR, "db.sqlite")
    SQLALCHEMY_ECHO = False  # print logs from sql-alchemy for dev and testing


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "tests/db.sqlite")
    # SQLALCHEMY_ECHO = True  # print logs from sql-alchemy for dev and testing


class ProductionConfig(BaseConfig):
    SKIP_SEED_USERS_AUTH_CHECKS = False
