# -*- coding: utf-8 -*-
from django.conf import settings as django_settings


SERVER = getattr\
    ( django_settings
    , 'JENKINS_SERVER_URI'
    , 'http://192.168.20.2:8080'
    )

TEMPLATE_PATTERN = getattr\
    ( django_settings
    , 'JENKINS_TEMPLATE_PATTERN'
    , '^template'
    )