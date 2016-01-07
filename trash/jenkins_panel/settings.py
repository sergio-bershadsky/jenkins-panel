import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '8r#52zfmfq1jyb@r=7e4eym5j)5k#+1a)%3y$qwk@p#he$6b7x'

DEBUG = bool(os.environ.get('DEBUG')) or False
DEBUG_PROPAGATE_EXCEPTIONS = DEBUG or False

ALLOWED_HOSTS = []

INSTALLED_APPS = \
    ( 'suit'
    , 'django.contrib.admin'
    , 'django.contrib.contenttypes'
    , 'django.contrib.sessions'
    , 'django.contrib.auth'
    , 'django.contrib.messages'
    , 'django.contrib.staticfiles'

    , 'jenkins_panel.apps.jenkins'
    )

MIDDLEWARE_CLASSES = \
    ( 'django.contrib.sessions.middleware.SessionMiddleware'
    , 'django.middleware.common.CommonMiddleware'
    , 'django.middleware.csrf.CsrfViewMiddleware'
    , 'django.contrib.auth.middleware.AuthenticationMiddleware'
    , 'django.contrib.auth.middleware.SessionAuthenticationMiddleware'
    , 'django.contrib.messages.middleware.MessageMiddleware'
    , 'django.middleware.clickjacking.XFrameOptionsMiddleware'
    , 'django.middleware.security.SecurityMiddleware'
    )

ROOT_URLCONF = 'jenkins_panel.urls'

TEMPLATES = \
    [ { 'BACKEND': 'django.template.backends.django.DjangoTemplates'
      , 'DIRS': []
      , 'APP_DIRS': True
      , 'OPTIONS':
        { 'context_processors':
          [ 'django.template.context_processors.debug'
          , 'django.template.context_processors.request'
          , 'django.contrib.auth.context_processors.auth'
          , 'django.contrib.messages.context_processors.messages'
    ] } } ]

WSGI_APPLICATION = 'jenkins_panel.wsgi.application'

DATABASES = \
    { 'default':
      { 'ENGINE': 'django.db.backends.mysql'
      , 'HOST': 'mysql'
      , 'NAME': os.environ["MYSQL_ENV_MYSQL_DATABASE"]
      , 'USER': os.environ["MYSQL_ENV_MYSQL_USER"]
      , 'PASSWORD': os.environ["MYSQL_ENV_MYSQL_PASSWORD"]
    } }

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

AUTHENTICATION_BACKENDS = \
    ( 'django.contrib.auth.backends.ModelBackend'
    , )

### SUIT ###

SUIT_CONFIG = \
    { 'ADMIN_NAME': u"Jenkins panel"
    , 'MENU_EXCLUDE':
        ( 'auth.group'
        , 'auth'
    )   }

### CAS ###

MIDDLEWARE_CLASSES = tuple(MIDDLEWARE_CLASSES) + ('cas.middleware.CASMiddleware', )

AUTHENTICATION_BACKENDS = tuple(AUTHENTICATION_BACKENDS) + ('django_cas_client_nsm.backends.CASBackend', )

if os.environ.get("AUTH_PORT_80_TCP_ADDR"):
    CAS_SERVER_URL = 'http://%s/cas/' % os.environ.get("AUTH_PORT_80_TCP_ADDR")
else:
    CAS_SERVER_URL = 'http://localhost:10000/cas/'

CAS_RESPONSE_CALLBACKS = \
    ( 'django_cas_client_nsm.callbacks.user_attributes_callback'
    , )

CAS_AUTO_CREATE_USER = False

### LOGGING ###

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'jsonrpc.manager': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
    },
}


JENKINS_TASKS = (
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.run_pyflakes',
)

PROJECT_APPS = \
    ( 'jenkins_panel.apps.jenkins'
    , )