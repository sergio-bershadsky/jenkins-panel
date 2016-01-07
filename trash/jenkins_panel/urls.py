# -*- coding: utf-8 -*-
from django.conf.urls import include, patterns
from django.contrib import admin


urlpatterns = patterns(''
    , (r'^admin/login/$', 'cas.views.login')
    , (r'^admin/logout/$', 'cas.views.logout')
    , (r'^admin/', include(admin.site.urls))
    )