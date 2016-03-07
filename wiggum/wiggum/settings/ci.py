from .wiggum import *

SECRET_KEY = '_24w(k$dpc856%!oesr8#zc0w0gd9d2hi)huda%euyxz574(pi'
DEBUG = True

#TODO: change dockerfile
MEDIA_ROOT = "/app/media"
STATIC_ROOT = '/app/static'

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


if TESTING:
    PIPELINE_ENABLED = False
    JWT_COOKIE_CLONE = False
    LANGUAGE_CODE = 'en-us'
    JWT_VERSION = 1
    JWT_MINIMUM_VERSION = 1

# Disable sentry
LOGGING['loggers']['']['handlers'] = None

JWT_SECRET_KEY = "wiggum_h23z2digzrv#a_8sh1p@8d0_7)q-h^77l1(+c)mi@%x5(er(w*"
JWT_VERIFICATION_KEY = JWT_SECRET_KEY

JWT_COOKIE_DOMAIN = "127.0.0.1"
JWT_COOKIE_DOMAIN_AUTO = True
JWT_COOKIE_DOMAIN_AUTO_LEVEL = 2
JWT_COOKIE_CLONE = False
JWT_COOKIE_CLONE_DOMAINS_ENDPOINT = (
    "dev.login.wiggum.com:8009",
    "dev.login.wiggum.io:8009",
    "dev.login.wiggum.org:8009",
)
JWT_ISSUER = "wiggumio_ci"

FORCE_LOGIN_FORM = False
PIPELINE_ENABLED = False

JWT_SET_PERMISSION_ON_TOKEN = True
