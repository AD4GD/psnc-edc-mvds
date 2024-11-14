# pylint:disable=E0602,E0611,E0012

from arguments import Group, Service
from arguments.network import wait_for_port
from arguments.types import Dict, Json, Ref, Str
from path import Path

settings_dir = Path(__file__).dirname()
base_dir = settings_dir.dirname()
project_dir = base_dir.dirname()


class ServiceSettings(Service):
    class API(Group):
        SERVICE_NAME = "edc-connector"
        SERVICE_DESCRIPTION = "EDC Connectors"
        SERVICE_VERSION = "v1.0.0"
        DEFAULT_DATE_TIME_FORMAT = "%y-%m-%d %H:%M:%S:%f"

    class Main(Group):
        DEBUG = False
        SECRET_KEY = "vl@^dt&+!2gbol*os@5=^=xx4(wz6c9*b-ch7+nffh7ab%*403"
        MAIN_DOMAIN = "localhost.edc.connector"
        SECONDARY_DOMAIN = Str(default=None)

    class Database(Group):
        DATABASE_ENGINE = "django.db.backends.postgresql_psycopg2"
        DATABASE_USER = Str(default="user")
        DATABASE_PASS = Str(default="pass")
        DATABASE_HOST = "postgres"
        DATABASE_PORT = 5432
        DATABASE_NAME = "main-db"
        DATABASE_CONN_MAX_AGE = 0
        # TODO DV-275: make this just {}
        DATABASE_OPTIONS = Dict(default={})
        DATABASE_TIME_ZONE = Str(default=None)

        WAIT_FOR_DATABASE = False
        WAIT_FOR_DATABASE_TIMEOUT = 10

    class Cache(Group):
        MEMCACHED_BACKEND = "common.cache.pymemcached.PyMemcacheImproved"
        MEMCACHED_HOST = ["memcached"]
        MEMCACHED_PORT = 11211
        MEMCACHED_IGNORE_EXC = True
        MEMCACHED_DEFAULT_NOREPLY = True
        MEMCACHED_KEY_PREFIX = ""
        # TODO DV-275: support queries

    class Logging(Group):
        DJANGO_LOG_LEVEL = "INFO"
        SERVICE_LOG_LEVEL = "DEBUG"

    class Deployment(Group):
        STATIC_ROOT = str(base_dir / "collected-static")
        SENTRY_DSN = Str(default=None)
        SENTRY_ENVIRONMENT = Str(default=Ref("MAIN_DOMAIN"))

    class CORS(Group):
        CORS_ORIGIN_ALLOW_ALL = True
        CORS_ALLOW_HEADERS = ["*"]
        CORS_ORIGIN_WHITELIST = []
        CORS_URLS_REGEX = r"^.*$"

    class Uwsgi(Group):
        # the default value SRV_UWSGI_GEVENT here should be kept in sync
        # with default values in:
        # docker/django/arguments/uwsgi/context.py
        # src/main/wsgi.py
        SRV_UWSGI_GEVENT = True
        _SRV_RUNNING_INSIDE_UWSGI = False

    class Auth(Group):
        AUTH_OPENID_PROVIDER = Str(default=None)
        AUTH_FAKE_OPENID_PROVIDER = "https://fake.login.demeter.org"
        AUTH_TOKEN_URL = Str(default=None)
        AUTH_AUTH_URL = Str(default=None)
        CLIENT_AUTH_HEADER_NAME = "X-CLIENT-TOKEN"
        AUTH_COOKIE_NAME = "auth"
        AUTH_HEADER_NAME = "Authorization"
        AUTH_HEADER_PREFIX = "Bearer"
        AUTH_KEYSTORE_CACHE = "locmem"
        AUTH_KEYSTORE_TIMEOUT = 24 * 60 * 60  # 24 hours
        AUTH_REQUESTS_TIMEOUT = 10.0  # seconds
        AUTH_REQUESTS_VERIFY = True
        AUTH_REQUIRED_CLAIMS = []
        AUTH_SUBJECT_CLAIM = "sub"
        AUTH_KEYS = Json(default={})
        AUTH_LEEWAY = 0
        AUTH_ADD_SECRET_KEY = True
        AUTH_AUD = Str(default=None)
        AUTH_CLIENT_ID = Str(default=None)
        AUTH_PASSWORD_LENGTH = 8
        AUTH_AUDIENCE_CLAIM = "aud"
        AUTH_FIRST_NAME_CLAIM = "given_name"
        AUTH_LAST_NAME_CLAIM = "family_name"
        AUTH_USERNAME_CLAIM = "preferred_username"
        AUTH_RESOURCES_ACCESS_CLAIM = "resource_access"
        AUTH_ROLES_CLAIM = "roles"
        AUTH_GUEST_USERNAME = "guest"

    class Security(Group):
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


SERVICE = ServiceSettings()

SERVICE.explode(globals())

wait_for_port(DATABASE_HOST, DATABASE_PORT, WAIT_FOR_DATABASE, WAIT_FOR_DATABASE_TIMEOUT)  # noqa:E0602


# Application definition

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django.contrib.contenttypes",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django_extensions",
    "watchman",
    "corsheaders",
    "common",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "common.auth.django.TokenAuthenticationMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "main.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "main.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": DATABASE_ENGINE,  # noqa:E0602
        "USER": DATABASE_USER,  # noqa:E0602
        "PASSWORD": DATABASE_PASS,  # noqa:E0602
        "HOST": DATABASE_HOST,  # noqa:E0602
        "PORT": DATABASE_PORT,  # noqa:E0602
        "NAME": DATABASE_NAME,  # noqa:E0602
        "ATOMIC_REQUESTS": False,
        "AUTOCOMMIT": True,
        "CONN_MAX_AGE": DATABASE_CONN_MAX_AGE,  # noqa:E0602
        "OPTIONS": DATABASE_OPTIONS,  # noqa:E0602
        "TIME_ZONE": DATABASE_TIME_ZONE,  # noqa:E0602
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
    "memcache": {
        "BACKEND": MEMCACHED_BACKEND,  # noqa:E0602
        "IGNORE_EXC": MEMCACHED_IGNORE_EXC,  # noqa:E0602
        "DEFAULT_NOREPLY": MEMCACHED_DEFAULT_NOREPLY,  # noqa:E0602
        "LOCATION": ["{}:{}".format(h, MEMCACHED_PORT) for h in MEMCACHED_HOST],  # pylint:disable=C0209 # noqa:E0602
        "KEY_PREFIX": MEMCACHED_KEY_PREFIX,  # noqa:E0602
    },
    "locmem": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}


# swagger
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "OAUTH2": {
            "type": "oauth2",
            "flow": "accessCode",
            "name": AUTH_HEADER_NAME,  # noqa:E0602,E221
            "in": "header",
            "tokenUrl": AUTH_TOKEN_URL,  # noqa:E0602,E221
            "authorizationUrl": AUTH_AUTH_URL,
            "scopes": "openid roles",
        },
        "Bearer": {"type": "apiKey", "name": AUTH_HEADER_NAME, "in": "header"},  # noqa:E0602,E221
        "Client": {"type": "apiKey", "name": CLIENT_AUTH_HEADER_NAME, "in": "header"},  # noqa:E0602
    }
}


# explicitly support SQS and RabbitMQ
# map VHOST into account_id
# map


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

# when changing this value, also uwsgi.ini has to be adjusted
# STATIC_URL = "/api/static/"


# Logging
# https://docs.djangoproject.com/en/1.11/topics/logging/

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[%(asctime)s] %(name)s:%(lineno)d %(levelname)s: %(message)s",
        },
        "console-server": {"format": "[%(asctime)s] %(message)s", "datefmt": "%d/%b/%Y:%H:%M:%S %z"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "console-server": {
            "class": "logging.StreamHandler",
            "formatter": "console-server",
        },
    },
    "loggers": {
        # this is ERROR here, because all other messages are in fact
        # duplicated by either django.server logger in runserver configuration
        # or by the uWSGI logging in production configuration
        "api": {
            "handlers": ["console"],
            "level": SERVICE_LOG_LEVEL,  # noqa:E0602,E221
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console-server"],
            "level": DJANGO_LOG_LEVEL,  # noqa
            "propagate": False,
        },
        "django": {
            "handlers": ["console"],
            "level": DJANGO_LOG_LEVEL,  # noqa
            "propagate": False,
        },
        "": {
            "handlers": ["console"],
            "level": DJANGO_LOG_LEVEL,  # noqa
        },
    },
}


# other django settings

ALLOWED_HOSTS = [MAIN_DOMAIN.split(":")[0]]  # noqa

if SECONDARY_DOMAIN:  # noqa
    ALLOWED_HOSTS.append(SECONDARY_DOMAIN.split(":")[0])  # noqa

# For localhost and tests
ALLOWED_HOSTS.append("django")

# 3-rd party settings

WATCHMAN_CHECKS = (
    "watchman.checks.databases",
    "watchman.checks.caches",
    "common.checks.django",
)

if SENTRY_DSN:  # pragma: no cover # noqa
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENVIRONMENT,
        integrations=[
            DjangoIntegration(),
        ],  # noqa
    )


# Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"

# TODO DV-790: Remove this ignoring, fix warnings in `manage-check` and verify if everything works
SILENCED_SYSTEM_CHECKS = [
    "security.W004",
    "security.W008",
]

# Other
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
