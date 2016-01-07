# -*- coding: utf-8 -*-
import json
import re

from collections import Mapping


def dict_get(data, path, default=None):
    segments = path.split('.')
    for s in segments:
        try:
            data = data[s]
        except (TypeError, KeyError):
            try:
                s = int(s)
                data = data[s]
                continue
            except (KeyError, IndexError, ValueError):
                pass
            return default
    return data


def dict_update(data, path, value):
    segments = path.split('.')
    inner_data = data
    for i, s in enumerate(segments, start=1):
        if i == len(segments):
            inner_data[s] = value
            break

        if not inner_data.has_key(s) or not issubclass(type(inner_data[s]), Mapping):
            inner_data[s] = {}
        inner_data = inner_data[s]

    return data


def pf_json(data):
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)


def upper2camel(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def dict_to_table(data):
    result = list()
    for key, value in data.iteritems():
        extract_value(result, value, key)

    return sorted(result, key=lambda v: v[0])


def make_key(*segments):
    return '.'.join(map(str, filter(lambda v: v is not None, segments)))


def extract_value(result, data, prefix=None):
    if issubclass(type(data), dict):
        extract_dict(result, data, prefix)
    elif issubclass(type(data), list):
        extract_list(result, data, prefix)
    else:
        key = prefix
        result.append((key, data))


def extract_dict(result, data, prefix=None):
    for key, value in data.iteritems():
        key = make_key(prefix, key)
        extract_value(result, value, prefix=key)


def extract_list(result, data, prefix=None):
    for i, value in enumerate(data):
        key = make_key(prefix, i)
        extract_value(result, value, prefix=key)


def get_by_path(path, instance, default=None):
    path = path.split('.')
    result = instance
    for segment in path:
        try:
            result = getattr(result, segment, None) or default
        except (AttributeError, KeyError):
            return default
    return result


def inner_formatter(self, context, model, name):
    return get_by_path(name, model)