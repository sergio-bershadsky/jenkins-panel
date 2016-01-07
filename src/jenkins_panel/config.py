# -*- coding: utf8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))


CSRF_ENABLED = True
SECRET_KEY = r'zY$}dhNsy^z4r8G%[\b8^+KV8a7(+U<p'
BABEL_DEFAULT_LOCALE = 'ru'

# available languages
LANGUAGES = \
    { 'en': 'English'
    , 'ru': 'Russian'
    }

# administrator list
ADMINS = \
    [ 'nikitinsm@gmail.com'
    , ]

MONGODB_SETTINGS = \
    { 'DB': 'jenkins_panel'
    , 'HOST': 'mongo'
    }

COLLECT_STATIC_ROOT = os.path.join(os.environ.get('APP_ROOT') or basedir, 'static')

JENKINS_SERVER_URI = 'http://192.168.20.2:8080'


MONGO_HOST = 'mongo'