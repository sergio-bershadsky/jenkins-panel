# -*- coding: utf-8 -*-
import logging

import wdb
import jenkins

from bson.objectid import ObjectId
from flask import redirect, url_for, flash, request
from flask_admin import expose
from flask_admin.actions import action
from werkzeug.datastructures import MultiDict
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

    # TODO
    @action('update', 'Update')
    def action_approve(self, ids):
        for model_id in ids:
            model = self.get_one(model_id)
            form_class = self.get_form()
            form = form_class\
                ( MultiDict()
                , csrf_enabled=False
                , **model
                )
            if self.validate_form(form):
                if self.update_model(form, model):
                    flash('Record %s was successfully saved.' % model_id)
            else:
                flash(form.errors, 'error')