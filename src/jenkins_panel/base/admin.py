# -*- coding: utf-8 -*-
from flask.ext.admin.contrib.pymongo import ModelView
from jenkins_panel.mongo import mongo

from . import utils


class BaseModelView(ModelView):

    collection_name = None

    def __init__(self, *args, **kwargs):
        collection = self.get_collection()
        super(BaseModelView, self).__init__(collection, *args, **kwargs)

    @classmethod
    def get_collection(cls, collection_name=None):
        view_name = utils.upper2camel(cls.__name__)
        app_label = cls.__module__.split('.')[-2]
        collection_name = app_label + '_' + (collection_name or cls.collection_name or view_name)
        return getattr(mongo.db, collection_name)