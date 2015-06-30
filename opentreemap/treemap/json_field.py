from django.contrib.gis.db import models
from django.utils.six import with_metaclass

from south.modelsinspector import add_introspection_rules

import json

from opentreemap.util import dotted_split
from DotDict import DotDict


class JSONField(with_metaclass(models.SubfieldBase, models.TextField)):
    def to_python(self, value):
        if isinstance(value, basestring):
            obj = json.loads(value or "{}")
            return DotDict(obj) if isinstance(obj, dict) else obj
        else:
            return value

    def get_prep_value(self, value):
        return json.dumps(value or {})

    def get_prep_lookup(self, lookup_type, value):
        # Contains lookups will generally work when looking for values
        if lookup_type in ('contains', 'icontains'):
            return super(JSONField, self).get_prep_lookup(lookup_type, value)
        raise TypeError("JSONField doesn't support lookups")

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)


add_introspection_rules([], ["^treemap\.json_field\.JSONField"])


def is_json_field_reference(field_path):
    return '.' in field_path


def _get_json_as_dotdict(model, field_path):
    field, json_path = dotted_split(field_path, 2, maxsplit=1)
    if not hasattr(model, field):
        raise ValueError('Field %s not found' % field_path)
    dotdict = getattr(model, field)
    if type(dotdict) is not DotDict:
        raise ValueError('Field %s does not contain JSON' % field_path)
    return dotdict, json_path


def get_attr_from_json_field(model, field_path):
    """
    Get specified value from a JSON field.
    For example, if field_name is "config.foo", get the JSON
    field "config" from the model and look up the value "foo".
    Deeper lookups also work, e.g. "config.foo.bar.baz".
    Returns None if the JSON path is not found.
    """
    dotdict, json_path = _get_json_as_dotdict(model, field_path)
    return dotdict.get(json_path, None)


def set_attr_on_json_field(model, field_path, value):
    """
    Set specified value on a JSON field (see get_attr_from_json_field)
    """
    dotdict, json_path = _get_json_as_dotdict(model, field_path)
    dotdict[json_path] = value
