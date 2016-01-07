# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DefaultConfig(AppConfig):
    name = 'jenkins_panel.apps.jenkins'
    verbose_name = _("Jenkins panel")