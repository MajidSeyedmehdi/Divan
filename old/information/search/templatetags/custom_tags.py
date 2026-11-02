
from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    if not dictionary:
        return None
    try:
        key = str(key)
        return dictionary.get(key)
    except Exception:
        return None