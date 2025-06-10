# esgdata/templatetags/custom_filters.py
from django import template
import os

register = template.Library()  # Fontos, hogy ez az objektum létezzen

@register.filter
def filename(value):
    if hasattr(value, 'name'):
        return os.path.basename(value.name)
    return ''

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    # Lehetne egy else ág, ami None-t vagy ''-t ad vissza,
    # vagy logol, ha nem dict a dictionary.
    # Most None-t ad vissza, ha nem dict, ami a sablonban
    # a `|default_if_none:""` miatt üres stringként jelenhet meg.
    return None