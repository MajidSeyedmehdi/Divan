from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key)




@register.filter
def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

@register.filter
def clean_rec_name(value):
    """پاک کردن نقل‌قول‌ها و پرانتزها و فاصله‌های اضافی از نام صدابردار"""

    if not value:
        return ""

    if not isinstance(value, str):
        value = str(value)

    return (
        value.replace("‘", "")
             .replace("’", "")
             .replace("'", "")
             .replace("(", "")
             .replace(")", "")
             .replace("،", "")
             .strip()
    )