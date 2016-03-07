import os
import sys

import raven

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE_MODULES_PATH = os.path.join(BASE_DIR, "..", "..", "node_modules", ".bin")
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

SECRET_KEY = None
DEBUG = False

ALLOWED_HOSTS = []

WIGGUM_VERSION = "0.1"

# Application definition

PRIORITY_THIRD_PARTY_APPS = ('django_admin_bootstrapped',)

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'rest_framework',
    'pipeline',
    'raven.contrib.django.raven_compat',
    'rest_framework_swagger',
    'django_prometheus',
)

LOCAL_APPS = (
    'users',
    'applications',
    'authorization',
    'themes',
    'administrator',
    'metrics',
)

# Load custom application to change wiggum logic
CUSTOM_APP = os.getenv('WIGGUM_CUSTOM_APP', None)
if CUSTOM_APP:
    CUSTOM_APP = (CUSTOM_APP,)
else:
    CUSTOM_APP = ()

INSTALLED_APPS = PRIORITY_THIRD_PARTY_APPS + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS + CUSTOM_APP


MIDDLEWARE_CLASSES = (
    'django_prometheus.middleware.PrometheusBeforeMiddleware', # Metrics start
    'authorization.middleware.WiggumValidCloneDomainMiddleware',
    'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'administrator.middleware.JWTAuthMiddleware',  # Custom middleware for jwt auth
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'administrator.middleware.AdminAuthorizationRedirectMiddleware', # Custom middleware for jwt auth
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware', # Metrics end
)

AUTHENTICATION_BACKENDS = (
    'administrator.backends.JWTAuthBackend',
)

ROOT_URLCONF = 'wiggum.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wiggum.wsgi.application'

DATABASES = {}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (os.path.join(BASE_DIR, "..", "locale"), )

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

USE_TZ = True

AUTH_USER_MODEL = 'users.User'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s] %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'sentry': {
            'level': 'WARNING',  # Only send to sentry warning, error and panic
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
    },
    'loggers': {
        # Root logger
        '': {
            'level': 'DEBUG',
            'handlers': ['sentry', ],
        },

        # Third party loggers
        'django': {
            'handlers': ['default'],
            'propagate': True,
            'level': 'INFO',
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['default'],
            'propagate': True,
        },

        # Local apps loggers
        'authorization': {
            'handlers': ['default'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'applications': {
            'handlers': ['default'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'users': {
            'handlers': ['default'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'themes': {
            'handlers': ['default'],
            'propagate': True,
            'level': 'DEBUG',
        },
    },
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'authorization.permissions.AppIsAuthenticated',
    )
}

# time handy  variables

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR

# Static stuff
STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "pipeline.finders.PipelineFinder",
)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)


# Django pipeline
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yuglify.YuglifyCompressor'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.uglifyjs.UglifyJSCompressor'

PIPELINE_CSS = {
    'default': {
        'source_filenames': (
            'bower/bootstrap/dist/css/bootstrap.css',
            # 'bower/bootstrap/dist/css/bootstrap-theme.css',
            'bower/fontawesome/css/font-awesome.css',
        ),
        'output_filename': 'css/default.min.css',
    },
    'wiggum': {
        'source_filenames': (
            'css/style.css',
        ),
        'output_filename': 'css/wiggum.min.css',
    },
    'login': {
        'source_filenames': (
            'css/login.css',
        ),
        'output_filename': 'css/login.min.css',
    },
    'admin': {
        'source_filenames': (
            'bower/bootstrap-multiselect/dist/css/bootstrap-multiselect.css',

        ),
        'output_filename': 'css/admin.min.css',
    },
    'error': {
        'source_filenames': (
            'css/404.css',
        ),
        'output_filename': 'css/error.min.css',
    }
}

PIPELINE_JS = {
    'default': {
        'source_filenames': (
            'bower/jquery/dist/jquery.js',
            'bower/bootstrap/dist/js/bootstrap.js'
        ),
        'output_filename': 'js/libs.min.js',
    },
    'admin': {
        'source_filenames': (
            'bower/bootstrap-multiselect/dist/js/bootstrap-multiselect.js',
        ),
        'output_filename': 'js/admin.min.js',
    },
    'easter-egg':{
        'source_filenames': (
            'js/konami.js',
            'js/easter-egg.js',
        ),
        'output_filename': 'js/easter-egg.min.js',
    },
    'modernizr':{
        'source_filenames': (
            'bower/modernizr/modernizr.js',
        ),
        'output_filename': 'js/modernizr.min.js',
    }
}

# Sentry configuration
RAVEN_CONFIG = {
    'dsn': None,
    'release': WIGGUM_VERSION,
    # Sanitize data
    'processors': (
        'raven.processors.SanitizePasswordsProcessor', )
}

# Swagger docs config

SWAGGER_SETTINGS = {
    'api_version': 'v1',
    'api_path': '/api/v1',
    'is_authenticated': True,
    'is_superuser': True,
}

# Admin redirect to our login to login with our own system
LOGIN_URL = "a/login"
