# -*- coding: utf-8 -*-
import wdb
import jenkins

from bson.objectid import ObjectId
from flask import redirect, url_for, flash
from flask.ext.admin import expose
from wtforms.widgets import HTMLString
from jenkins_panel import config

from ..base.admin import BaseModelView
from . import forms


client = jenkins.Jenkins(config.JENKINS_SERVER_URI)


class JobAdminView(BaseModelView):
    collection_name = 'job'
    form = forms.JobForm

    column_list = \
        ( 'label'
        , 'description'
        , 'play_btn'
        )

    def play_btn_formatter(self, context, model, name):
        btn = """
<a class="btn btn-primary pull-right" href="%s">
    <span class="fa fa-play glyphicon glyphicon-play"></span>
</a>""" % url_for('.run_job', pk=model.get('_id'))

        return HTMLString(btn)

    column_formatters = {
        'play_btn': play_btn_formatter
    }

    @expose('/run/<pk>')
    def run_job(self, pk):
        #TODO: ajax call
        job = self.coll.find_one({'_id': ObjectId(pk)})
        name = 'auto-' + job.get('name')
        client.build_job(name)
        info = client.get_job_info(name)
        flash(HTMLString(u'Сборка "%s" запущена <a href="%s" target="_blank">подробнее</a>' % (name, info.get('url'))))
        return redirect(url_for('.index_view'))