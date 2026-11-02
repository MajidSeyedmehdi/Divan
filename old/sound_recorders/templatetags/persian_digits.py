from django import template

register = template.Library()

EN_TO_FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

@register.filter
def persian_digits(value):
    """تبدیل اعداد انگلیسی به فارسی"""
    if value is None:
        return ""
    return str(value).translate(EN_TO_FA)
