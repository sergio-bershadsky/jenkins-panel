# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.html import escape
from django.forms import widgets
from django.utils.safestring import mark_safe

from . import models


class ParamsFormWidget(widgets.MultiWidget):
    """
    @note: Гавнокод - когда-нибудь, что-нибудь надо с этим сделать
    """

    def __init__(self, form, attrs=None):
        widgets = []
        form = form()

        for field in form:
            widget = field.field.widget
            widget.attrs['field'] = field
            widgets.append(widget)

        super(ParamsFormWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        value = value.split('\n')
        value = map(lambda v: v.split('=')[-1], value)
        return value

    def value_from_datadict(self, data, files, name):
        values = super(ParamsFormWidget, self).value_from_datadict(data, files, name)
        result = []
        for i, value in enumerate(values):
            widget = self.widgets[i]
            if type(value) is bool:
                value = str(value).lower()
            result.append(widget.attrs['field'].label + '=' + str(value))
        return '\n'.join(result)

    def render(self, name, value, attrs=None):
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        output.append('<table class="table table-striped table-bordered table-hover table-condensed" style="width: 50%; margin: 0">')
        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None

            field = widget.attrs.pop('field', None)

            final_attrs['style'] = 'width: auto'
            if type(widget) in (widgets.CheckboxInput, ):
                if widget_value == 'false':
                    widget_value = None

            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))

            output.append('<tr>')
            output.append('<td style="width: 30%">')
            if field:
                output.append('<label>%s</label>' % field.label)
            output.append('</td>')
            output.append('<td>')
            output.append(widget.render(name + '_%s' % i, widget_value, final_attrs))
            if field.help_text:
                output.append('<p class="help-block">')
                output.append(field.help_text)
                output.append('</p>')
            output.append('</td>')
            output.append('<tr>')
        output.append('</table>')
        return mark_safe(self.format_output(output))


@admin.register(models.View)
class ViewAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = \
        ( '__unicode__'
        , 'get_params'
        #, 'get_config_html'
        )
    fieldsets = (
        (None, {
            'fields': ('label', 'name', 'parents', 'nodes')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('description', 'params'),
        }),
    )

    def get_config_html(self, instance):
        return '<pre>%s</pre>' % escape(instance.get_config())
    get_config_html.allow_tags = True

    def get_params(self, instance):
        return '<pre>%s</pre>' % escape(instance.params)
    get_params.allow_tags = True

    # def get_params_form(self, instance):
    #     return '<table>%s</table>' % instance.get_params_form()().as_table()
    # get_params_form.allow_tags = True

    def get_form(self, request, obj=None, **kwargs):
        result = super(ProjectAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            params_field = result.base_fields['params']
            params_field.widget = ParamsFormWidget(obj.get_params_form())
        return result



# Unregister auth

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

admin.site.unregister(User)
admin.site.unregister(Group)