# -*- coding: utf-8 -*-
import os
import flask
import flask_admin

from jenkins_panel.mongo import mongo
from jenkins_panel.storage.admin import JobAdminView

from .debug import Wdb


#######
# APP #
#######

app = flask.Flask('jenkins_panel')
app.config.from_object('jenkins_panel.config')

mongo.init_app(app)


#########
# DEBUG #
#########

if 'DEBUG' in os.environ:
    app.debug = True
    wdb = Wdb()
    #wdb.init_app(app)


with app.app_context():
    # Admin bundle
    admin = flask_admin.Admin\
        ( app
        , name=u"Jenkins panel"
        , template_mode="bootstrap3"
        , base_template="jenkins_panel/master.html"
        #, index_view=AuthView(url='/')
        )

    admin.add_view\
        ( JobAdminView()
        )

