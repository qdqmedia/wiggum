from .wiggum import *

SECRET_KEY = '8hcmch1@o&a5bjsx_56x5e4(gmc-6!g48x**usqelv_r9ok_-!'
DEBUG = True

# This will set the neccessary settings to use not debug on local without
# messing around with collectstatic and stuff
# Note: Cant guarantee everything will work as espected
# (use --insecure option on runserver to serve static files)
DEBUG_NOT_DEBUG = False

# TODO: change dockerfile
MEDIA_ROOT = "/app/media"
STATIC_ROOT = '/app/static'

INSTALLED_APPS += (
    'django_extensions',
    'debug_toolbar',
)

# Only add dev migrations when no tests are executing
if not TESTING:
    INSTALLED_APPS += ('dev_migrations', )  # Only for dev initial data

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
}

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'wiggum',
        'PASSWORD': 'clancy_wiggum',
        'HOST': os.getenv('DB_PORT_5432_TCP_ADDR', "127.0.0.1"),
        'PORT': os.getenv('DB_PORT_543_TCP_PORT', '5432'),
    },
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'wiggum',
    }
}

# Logging
LOGGING['formatters']['colored'] = {
    '()': 'colorlog.ColoredFormatter',
    'format': "%(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)s",
    'reset': True,
    'log_colors': {
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    },
    'style': '%'
}
LOGGING['handlers']['default']['formatter'] = "colored"


# Disable sentry
LOGGING['loggers']['']['handlers'] = None


JWT_SECRET_KEY = "wiggum_$*xb^9)!2q&*htl-x%wu!!hz6m!74@!22q$kho1jkb6ps8nr2k"
JWT_VERIFICATION_KEY = JWT_SECRET_KEY
JWT_SIGN_ALGORITHM = "HS256"

JWT_COOKIE_DOMAIN = "127.0.0.1"
JWT_COOKIE_DOMAIN_AUTO = True
JWT_COOKIE_DOMAIN_AUTO_LEVEL = 2
JWT_COOKIE_CLONE = True
JWT_COOKIE_CLONE_DOMAINS_ENDPOINT = (
    "dev.login.wiggum.com:8009",
    "dev.login.wiggum.io:8009",
    "dev.login.wiggum.org:8009",
)
JWT_ISSUER = "wiggumio_dev"
JWT_TRANSITION_ENABLE = False

FORCE_LOGIN_FORM = False


JWT_SET_PERMISSION_ON_TOKEN = False


if TESTING:
    FORCE_LOGIN_FORM = False
    PIPELINE_ENABLED = False
    JWT_COOKIE_CLONE = False
    LANGUAGE_CODE = 'en-us'
    JWT_VERSION = 1
    JWT_MINIMUM_VERSION = 1


# Should be the last part
if DEBUG_NOT_DEBUG:
    DEBUG = False
    ALLOWED_HOSTS = [
        "*"
    ]
    PIPELINE_ENABLED = False
    PIPELINE_COMPILERS = []
    PIPELINE_CSS_COMPRESSOR = []
    PIPELINE_JS_COMPRESSOR = []
    STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'
