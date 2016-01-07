# -*- coding: utf-8 -*-
import hashlib
import wdb
import jenkins
import xml.etree.cElementTree as etree

from mongoengine import fields, DynamicEmbeddedDocument

from jenkins_panel import config
from jenkins_panel.mongo import db


client = jenkins.Jenkins(config.JENKINS_SERVER_URI)


class KeyValue(db.EmbeddedDocument):
    key = fields.StringField\
        ( max_length=32
        )
    value = fields.StringField\
        ( max_length=32
        )


class JenkinsTemplateChoices(object):

    @property
    def jobs(self):
        return [item['name'] for item in client.get_jobs() if 'template' in item['name']]

    def __iter__(self):
        return self.jobs.__iter__()

    def __getitem__(self, item):
        return self.jobs[item]


class JenkinsNodeChoices(object):

    @property
    def nodes(self):
        return [item['name'] for item in client.get_nodes()]

    def __iter__(self):
        return self.nodes.__iter__()

    def __getitem__(self, item):
        return self.nodes[item]


class JenkinsTemplate(fields.EmbeddedDocument):
    name = fields.StringField\
        ( choices=JenkinsTemplateChoices()
        )


class Jenkins(fields.EmbeddedDocument):

    def __init__(self, *args, **kwargs):
        """
        @todo: move to field
        @todo: create cool widget
        """
        super(Jenkins, self).__init__(*args, **kwargs)
        source_params = {}
        jenkins_params = self.get_params_form_data()
        if jenkins_params:
            jenkins_params = {item['name']: item['initial'] or '' for item in jenkins_params}
            try:
                source_params = dict\
                    ( tuple
                      ( filter
                        ( lambda v: bool(v)
                        , map
                          ( lambda v: v.split('='), (self.param or '').split('\n'))
                        ) or {}
                      )
                    )
            except Exception as e:
                pass
            jenkins_params.update(source_params)
            self.param = '\n'.join(['='.join(map(str, [k, v])) for k, v in jenkins_params.iteritems()])


    signature = fields.StringField\
        ( max_length=64
        )
    parent = fields.ListField\
        ( fields.StringField
          ( max_length=64
          , choices=JenkinsTemplateChoices()
          )
        , required=True
        )
    node = fields.ListField\
        ( fields.StringField
          ( max_length=64
          , choices=JenkinsNodeChoices()
          )
        , required=True
        )
    param = fields.StringField\
        ()

    def get_config(self):
        if self.parent:
            # TODO: multiple inheritance
            xml_config = client.get_job_config(self.parent[0])
            if not xml_config:
                return

            xml_config = xml_config.encode('utf-8')
            # TODO: merge multiple configs
            self.signature = hashlib.sha256(xml_config).hexdigest()
            return xml_config

    def get_params_form_data(self):
        result = []
        type_mapping = \
            { 'hudson.model.StringParameterDefinition': ('StringField', {})
            , 'hudson.model.TextParameterDefinition': ('StringField', {})
            , 'hudson.model.BooleanParameterDefinition': ('BooleanField', {})
            , 'hudson.model.ChoiceParameterDefinition': ('StringField', {})
            }
        xml_config = self.get_config()
        if not xml_config:
            return
        tree = etree.fromstring(xml_config)
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


class Job(db.Document):
    label = fields.StringField\
        ( max_length=64
        , required=True
        )
    name = fields.StringField\
        ( max_length=64
        , required=True
        , unique=True
        )
    description = fields.StringField()
    jenkins = fields.EmbeddedDocumentField\
        ( Jenkins
        )

    def __unicode__(self):
        return "{0} ({1})".format(self.label, self.name)