# -*- coding: utf-8 -*-
import hashlib
import jenkins
import flask_wtf as form
import wdb


from lxml import etree
from flask.ext.admin.model.fields import InlineFormField, InlineFieldList
from wtforms import fields, validators, widgets, ValidationError
from jenkins_panel import config

client = jenkins.Jenkins(config.JENKINS_SERVER_URI)


class JenkinsViewChoices(object):

    def __iter__(self):
        return ((item['name'], item['name']) for item in ([{'name': ''}] + client.get_views()) if 'all' not in item['name'].lower())


class JenkinsParentChoices(object):

    def __iter__(self):
        return ((item['name'], item['name']) for item in client.get_jobs() if 'template' in item['name'])


class JenkinsNodeChoices(object):

    def __iter__(self):
        return ((item['name'], item['name']) for item in client.get_nodes())


class ReadonlyTextInput(widgets.TextInput):

    def __call__(self, field, **kwargs):
        kwargs.setdefault('readonly', 'readonly')
        return super(ReadonlyTextInput, self).__call__(field, **kwargs)


class ReadonlyTextArea(widgets.TextArea):

    def __call__(self, field, **kwargs):
        kwargs.setdefault('readonly', 'readonly')
        kwargs.setdefault('rows', '20')
        return super(ReadonlyTextArea, self).__call__(field, **kwargs)


class ParentForm(form.Form):
    name = fields.SelectField\
        ( choices=JenkinsParentChoices()
        )


def get_config(form_instance):
    if not form_instance.parent.data:
        return ''

    job_name = form_instance.parent.data[0]['name']

    # TODO: multiple inheritance
    try:
        xml_config = client.get_job_config(job_name)
    except jenkins.NotFoundException:
        return

    if not xml_config:
        return

    xml_config = xml_config.encode('utf-8')
    # TODO: merge multiple configs
    form_instance.signature = hashlib.sha256(xml_config).hexdigest()
    return xml_config


def get_params_data(form_instance):
    result = []
    type_mapping = \
        { 'hudson.model.StringParameterDefinition': ('StringField', {})
        , 'hudson.model.TextParameterDefinition': ('StringField', {})
        , 'hudson.model.BooleanParameterDefinition': ('BooleanField', {})
        , 'hudson.model.ChoiceParameterDefinition': ('SelectField', {})
        }
    xml_config = get_config(form_instance)
    if not xml_config:
        return result

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
            choices = [(node.text, node.text) for node in param.findall('choices/a/string')]
            if choices:
                choices = [('', u'варианты'), ] + choices

            result.append\
                ( { 'name': name
                  , 'type': field_type
                  , 'description': getattr(param.find('description'), 'text', None)
                  , 'default': getattr(param.find('defaultValue'), 'text', None)
                  , 'choices': choices
                  , 'kwargs': kwargs
                } )

    return result


def jenkins_param_form_factory(form_instance):
    attributes = {}
    for field in get_params_data(form_instance):
        kwargs = \
            { 'description': field['description']
            , 'default': field['default']
            }
        kwargs.update(field['kwargs'])
        if field['choices']:
            kwargs['choices'] = field['choices']
        attributes[field['name']] = getattr(fields, field['type'])(**kwargs)

    return type('Form', (form.Form, ), attributes)


def jenkins_form_factory(*args, **kwargs):
    attributes = dict\
        ( signature = fields.HiddenField\
            ()
        , view = fields.SelectField\
            ( u'вид'
            , choices=JenkinsViewChoices()
            , default=None
            )
        , parent = InlineFieldList\
            ( InlineFormField
              ( ParentForm
              )
            , label=u'родители'
            , description=u'порядок наследования важен'
            , validators=
              [ validators.DataRequired()
              , ]
            )
        , node = fields.SelectField\
            ( u'узлы'
            , choices=JenkinsNodeChoices()
            , validators=
              [ validators.DataRequired()
              , ]
            )
        , config = fields.StringField\
            ( u'конечный конфиг'
            , widget=ReadonlyTextArea()
        )   )

    form_instance = type('Form', (form.Form, ), attributes)(*args, **kwargs)
    if form_instance.parent.data:
        attributes['param'] = InlineFormField\
            ( jenkins_param_form_factory(form_instance)
            , u'Параметры'
            )

    return type('Form', (form.Form, ), attributes)(*args, **kwargs)


class JobForm(form.Form):

    name = fields.StringField\
        ( validators=
          [ validators.DataRequired()
          , validators.Regexp(r'^[a-z]+[a-z0-9-]+[a-z0-9]+$')
          ]
        , filters=
          [ lambda v: (v or '').lower()
          , ]
        )
    label = fields.StringField\
        ( validators=
          [ validators.DataRequired()
          , ]
        )
    description = fields.TextAreaField\
        ()
    jenkins = InlineFormField\
        ( jenkins_form_factory
        , label=u'настройки'
        )

    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        if 'name' in kwargs:
            self.name.widget = ReadonlyTextInput()

    def validate(self):


        result = super(JobForm, self).validate()
        if not result:
            return result

        jenkins_form = self.jenkins.form
        parent_config_xml = get_config(jenkins_form)
        parent_config_tree = etree.fromstring(parent_config_xml)

        # Enable
        disabled = parent_config_tree.find('disabled')
        disabled.text = 'false'

        # Inject description
        description = parent_config_tree.find('description')
        description.text = self.description.data

        # Assign slave
        can_roam = parent_config_tree.find('canRoam')
        can_roam.text = 'false'
        assigned_node = parent_config_tree.find('assignedNode')
        if not assigned_node:
            assigned_node = etree.SubElement(parent_config_tree, 'assignedNode')
        assigned_node.text = self.jenkins.node.data

        # Inject params
        param_txt = '\n'.join(['='.join(map(unicode, [k, v])) for k, v in (self.jenkins.data.get('param') or {}).iteritems() if v])
        env_xml = """
    <EnvInjectJobProperty plugin="envinject@1.92.1">
        <info>
            <propertiesContent>%s</propertiesContent>
            <loadFilesFromMaster>false</loadFilesFromMaster>
        </info>
        <on>true</on>
        <keepJenkinsSystemVariables>true</keepJenkinsSystemVariables>
        <keepBuildVariables>true</keepBuildVariables>
        <overrideBuildParameters>false</overrideBuildParameters>
        <contributors/>
    </EnvInjectJobProperty>""" % param_txt

        property_tree = parent_config_tree.find('properties')
        env_xml_tree = etree.fromstring(env_xml)
        property_tree.append(env_xml_tree)

        # Remove params section
        for item in parent_config_tree.xpath("properties/hudson.model.ParametersDefinitionProperty"):
            item.getparent().remove(item)


        # Finalize
        name = 'auto-' + self.name.data

        try:
            test_name = client.get_job_name(name)
        except jenkins.JenkinsException as e:
            raise ValidationError(e.message)

        final_config = etree.tostring(parent_config_tree)

        if not test_name:
            client.create_job(name, final_config)
        else:
            client.reconfig_job(name, final_config)

        self.jenkins.config.data = final_config

        # Add to view
        view = self.data['jenkins']['view']
        if view:
            view_config_xml = client.get_view_config(view).encode('utf-8')
            view_config_tree = etree.fromstring(view_config_xml)

            view_jobs = set()
            for item in view_config_tree.findall('jobNames/string'):
                view_jobs.add(item.text)
                item.getparent().remove(item)

            if name not in view_jobs:
                view_jobs.add(name)
                view_jobs = list(sorted(view_jobs))
                job_names_tree = view_config_tree.find('jobNames')
                for job_name in view_jobs:
                    record_tree = etree.SubElement(job_names_tree, 'string')
                    record_tree.text = job_name

                client.reconfig_view(view, etree.tostring(view_config_tree))

            #wdb.set_trace()
            #for item in view_config_tree.findall('jobames/string'):

        return result