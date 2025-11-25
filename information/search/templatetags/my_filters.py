from django import template

register = template.Library()

@register.filter
def get(d, key):
    if not d:
        return {}
    return d.get(key, {})