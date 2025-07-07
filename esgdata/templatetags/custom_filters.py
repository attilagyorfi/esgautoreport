# esgdata/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Lehetővé teszi, hogy egy szótárban kulcs alapján keressünk a sablonban."""
    return dictionary.get(key)