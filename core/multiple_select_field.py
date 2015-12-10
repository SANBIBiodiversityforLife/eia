"""
Field with multiple *static* choices (not via m2m)

Value is stored in DB as comma-separated values
Default widget is forms.CheckboxSelectMultiple
Python value: list of values

Original Django snippet: https://djangosnippets.org/snippets/1200/
It's 6 years old and doesn't work with latest Django
Also it implements 'max_choices' functionality - I have removed it for simplicity
"""

from django import forms
from django.db import models
from django.core import exceptions
from django.utils.encoding import force_text
# from south.modelsinspector import add_introspection_rules


class MultipleSelectFormField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple


class MultipleSelectField(models.Field):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "CharField"

    def get_choices_default(self):
        return self.get_choices(include_blank=False)

    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {
            'required': not self.blank,
            'label': self.verbose_name.capitalize(),
            'help_text': self.help_text,
            'choices': self.choices
        }

        if self.has_default():
            defaults['initial'] = self.get_default()

        defaults.update(kwargs)

        return MultipleSelectFormField(**defaults)

    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, list):
            return ",".join(map(unicode, value))
        if value is None or isinstance(value, basestring):
            return value
        else:
            return unicode(value)

    def to_python(self, value):
        if value is None or isinstance(value, list):
            return value
        else:
            return unicode(value).split(",")

    def validate(self, value, model_instance):
        if not self.editable:
            # Skip validation for non-editable fields.
            return

        if self._choices and value not in self.empty_values:
            if not isinstance(value, list):
                value = [value]
            if set(dict(self.choices).keys()) & set(value) == set(value):
                return
            raise exceptions.ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice',
                params={'value': value},
            )

        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages['null'], code='null')

        if not self.blank and value in self.empty_values:
            raise exceptions.ValidationError(self.error_messages['blank'], code='blank')

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(MultipleSelectField, self).contribute_to_class(cls, name)

        if self.choices:
            fieldname = self.name
            choicedict = dict(self.choices)

            def func(self):
                value = getattr(self, fieldname)
                if not isinstance(value, list):
                    value = [value]
                return ", ".join([force_text(choicedict.get(i, i)) for i in value])

            setattr(cls, 'get_%s_display' % fieldname, func)

# Provide South support
#add_introspection_rules([], ["^app_name\.fields\.MultipleSelectField"])
