import logging
import os
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy
from flask_marshmallow import Marshmallow
from flask_caching import Cache
from flask_cors import CORS
from flask_praetorian import Praetorian
from flask_migrate import Migrate
from flask_compress import Compress
from flask_socketio import SocketIO
from flask_profiler import Profiler
import socketio
from celery import Celery

from flask_admin import Admin
from flask_basicauth import BasicAuth

from ecom.constants import CACHE_CLEAR_SAFE_SUFFIX, CACHE_INDEFINETLY
import os
from werkzeug.middleware.profiler import ProfilerMiddleware
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address


class SQLAlchemy(_BaseSQLAlchemy):
    def apply_pool_defaults(self, app, options):
        super(SQLAlchemy, self).apply_pool_defaults(app, options)
        options["pool_pre_ping"] = True
        return options


db = SQLAlchemy()
mm = Marshmallow()
cache = Cache()
guard = Praetorian()
compress = Compress()
socketio = SocketIO()
profiler = Profiler()

admin = Admin(url="/api/admin")
basic_auth = BasicAuth()


CACHE_SECRET = os.getenv("CACHE_SECRET", "")
CACHE_HOST = os.getenv("CACHE_HOST", default="127.0.0.1")
CACHE_PORT = int(os.getenv("CACHE_PORT", default="6379"))
CACHE_DB = int(os.getenv("CACHE_DB", default="0"))

# limiter = Limiter(
#     app=app,
#     storage_uri=f"redis://:{CACHE_SECRET}@{CACHE_HOST}:{CACHE_PORT}/{CACHE_DB}",
#     key_func=get_remote_address,
#     default_limits=["1000000/day;5000000/hour;100000/minute"],
# )


def make_celery():
    celery = Celery(
        "ecom", backend=os.getenv("result_backend"), broker=os.getenv("broker_url")
    )
    return celery


celery = make_celery()


def init_celery(app):
    print(celery)
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask


def init_extensions(app):
    # sqlalchecmy
    # with app.app_context():
    db.init_app(app)

    # marshmallow
    mm.init_app(app)

    # flask caching
    cache.init_app(app)

    # Flask Admin
    admin.init_app(app)
    basic_auth.init_app(app)
    compress.init_app(app)
    socketio.init_app(app)

    # Currently Stopping Limit
    # limiter.init_app(app)

    # Monkey Patching Cache function to handle exception at central place
    cache_get = cache.get
    cache_set = cache.set
    cache_clear = cache.clear
    _cache_cache = cache.cache

    def get_from_cache(key):
        try:
            return cache_get(key)
        except Exception:
            logging.error("Not able to get value from cache - %s", key)
            return None

    def set_to_cache(key, value, timeout=CACHE_INDEFINETLY):
        try:
            cache_set(key, value, timeout)
            logging.info("Cache set successfully - %s", key)
        except Exception:
            logging.error("Not able to set value in cache - %s", key)

    def clear_cache(**kwargs):
        try:
            k_prefix = _cache_cache.key_prefix
            keys = _cache_cache._write_client.keys(k_prefix + "*")
            keys = [k.decode("utf8") for k in keys]
            keys = [
                k.replace(k_prefix, "")
                for k in keys
                if CACHE_CLEAR_SAFE_SUFFIX not in k
            ]
            cache.delete_many(*keys, **kwargs)
            logging.info("Cache Cleared.")
        except Exception as exc:
            logging.error("Not able to clear cache. Exception : %s" % (exc))

    cache.get = get_from_cache
    cache.set = set_to_cache
    cache.clear = clear_cache

    # flask-profiler werkzeug
    ## uncomment for code profiling
    if app.config["RUN_PROFILER"] is True:
        path_to_write = os.path.join("ecom", "profile")
        app.wsgi_app = ProfilerMiddleware(
            app.wsgi_app, restrictions=[0], profile_dir="ecom/profile"
        )
        if app.config["APP_DB_USE_SSL"]:
            connection_uri = (
                app.config["SQLALCHEMY_DATABASE_URI"] + "?" + "ssl_verify_cert=true"
            )
        else:
            connection_uri = app.config["SQLALCHEMY_DATABASE_URI"]

        # You need to declare necessary configuration to initialize
        # flask-profiler as follows:
        profiler.init_app(app)
        app.config["flask_profiler"] = {
            "enabled": app.config["RUN_PROFILER"],
            "storage": {
                "engine": "sqlite"
                # "engine": "sqlalchemy",
                # "db_url": connection_uri
                # +"?"+str(ssl_connection)
                # +str(ssl_connection)
                # +"?ssl_ca=C:\\projects\\sofac\\azure database\\BaltimoreCyberTrustRoot.crt.pem"
            },
            "basicAuth": {"enabled": True, "username": "admin", "password": "password"},
            "ignore": [
                "^/static/.*"
            ],
            "endpointRoot": "api/profiler",
        }

    # migration
    Migrate(app, db)

    CORS(app)


def get_redis_cache():
    return cache
