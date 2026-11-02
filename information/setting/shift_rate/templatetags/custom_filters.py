# main/templatetags/custom_filters.py
from django import template
from django.utils.safestring import mark_safe
import locale

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    دریافت مقدار از دیکشنری با کلید
    استفاده: {{ my_dict|get_item:my_key }}
    """
    if not isinstance(dictionary, dict):
        return ''

    # تبدیل کلید به string برای جستجو
    key_str = str(key)

    # اول با string دقیق چک کن
    if key_str in dictionary:
        return dictionary[key_str]

    # اگر کلید عددی است، با int هم چک کن
    try:
        key_int = int(key)
        if key_int in dictionary:
            return dictionary[key_int]
    except (ValueError, TypeError):
        pass

    return ''


@register.filter
def intcomma(value, use_farsi_separator=True):
    """
    فرمت اعداد با جداکننده هزارگان
    استفاده: {{ price|intcomma }} یا {{ price|intcomma:False }}
    """
    if value is None:
        return ''

    try:
        # تبدیل به عدد
        if isinstance(value, str):
            # حذف جداکننده‌های قبلی
            value = value.replace(',', '').replace('٬', '')

        num = float(value) if '.' in str(value) else int(value)

        # فرمت با جداکننده
        formatted = f"{num:,.0f}"

        # اگر جداکننده فارسی می‌خواهیم
        if use_farsi_separator:
            formatted = formatted.replace(",", "٬")

        return formatted
    except (ValueError, TypeError):
        return str(value)


@register.filter
def multiply(value, arg):
    """ضرب دو عدد"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """تقسیم دو عدد"""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def to_str(value):
    """تبدیل به رشته"""
    return str(value)


@register.filter
def default_if_none(value, default_value):
    """مقدار پیش‌فرض اگر None باشد"""
    return value if value is not None else default_value


@register.filter(name='range')
def filter_range(count):
    """ایجاد رنج اعداد"""
    return range(int(count))


@register.filter
def add_class(field, css_class):
    """اضافه کردن کلاس CSS به فیلد فرم"""
    return field.as_widget(attrs={"class": css_class})


@register.filter
def get_type(value):
    """دریافت نوع متغیر"""
    return type(value).__name__

@register.filterdef
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key)