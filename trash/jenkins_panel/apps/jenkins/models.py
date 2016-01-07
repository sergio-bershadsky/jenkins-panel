# -*- coding: utf-8 -*-
import hashlib
import xml.etree.cElementTree as etree

from django import forms
from django.core import validators
from django.db import models
from django.forms import fields
from django.utils.translation import ugettext as _
from jenkins import EMPTY_CONFIG_XML, NotFoundException

from .client import client
from . import settings


class View(models.Model):

    class Meta:
        verbose_name = _(u"Вид (группа)")
        verbose_name_plural = _(u"Виды (группы)")

    label = models.CharField\
        ( max_length=64
        )
    description = models.TextField\
        ()


class ProjectQuerySet(models.QuerySet):
    pass


class Project(models.Model):

    class Meta:
        verbose_name = _(u"Проект")
        verbose_name_plural = _(u"Проекты")

    objects = ProjectQuerySet.as_manager()

    signature = models.CharField\
        ( max_length=64
        , editable=False
        )
    label = models.CharField\
        ( max_length=64
        )
    name = models.CharField\
        ( max_length=32
        , validators=
          [ validators.RegexValidator(r'^[a-z]+[a-z-]*[a-z]?$')
          ]
        )
    description = models.TextField\
        ( max_length=64
        , null=True
        , blank=True
        )
    parents = models.CharField\
        ( max_length=64
        )
    nodes = models.CharField\
        ( max_length=64
        )
    params = models.TextField\
        ( null=True
        , blank=True
        )

    def __unicode__(self):
        return u'%s (%s)' % (self.label, self.get_name())

    def get_name(self):
        return 'auto-%s' % self.name

    def get_config(self):
        # TODO: multiple inheritance
        config = client.get_job_config(self.parents)
        # TODO: merge multiple configs
        return config


    def update(self):
        config = self.get_config()
        config_signature = hashlib.sha256(config).hexdigest()
        if self.signature == config_signature:
            return

        try:
            client.get_job_info(self.get_name())
        except NotFoundException:
            client.create_job(self.get_name(), EMPTY_CONFIG_XML)

        client.reconfig_job(self.get_name(), config)

        self.signature = config_signature

    def build(self):
        client.build_job(self.get_name())

    def get_params_form_data(self):
        result = []
        type_mapping = \
            { 'hudson.model.StringParameterDefinition': ('CharField', {})
            , 'hudson.model.TextParameterDefinition': ('CharField', {'widget': forms.widgets.Textarea})
            , 'hudson.model.BooleanParameterDefinition': ('BooleanField', {})
            , 'hudson.model.ChoiceParameterDefinition': ('ChoiceField', {})
            }
        config = self.get_config().encode('utf-8')
        #parser = etree.XMLParser(encoding="utf-8")
        tree = etree.fromstring(config)
        params_root = tree.findall('properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions')
        if params_root:
            params = params_root[0].getchildren()
            for param in params:
                name = getattr(param.find('name'), 'text', None)
                if not name:
                    continue

                field_type, kwargs = type_mapping.get(param.tag, None)
                if not type:
                    continue

                result.append\
                    ( { 'name': name
                      , 'type': field_type
                      , 'description': getattr(param.find('description'), 'text', None)
                      , 'initial': getattr(param.find('defaultValue'), 'text', None)
                      , 'choices': [(node.text, node.text) for node in param.findall('choices/a/string')]
                      , 'kwargs': kwargs
                    } )
        return result

    def get_params_form(self):
        data = self.get_params_form_data()
        attrs = {}
        for item in data:
            kwargs = item['kwargs']
            kwargs.update\
                ( { 'initial': item['initial']
                  , 'help_text': item['description']
                } )
            if item['choices']:
                kwargs.update({'choices': item['choices']})
            attrs[item['name']] = getattr(fields, item['type'])(**kwargs)
        return type('ParamForm', (forms.Form, ), attrs)


    def save(self, *args, **kwargs):
        self.update()
        return super(Project, self).save(*args, **kwargs)