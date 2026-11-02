from django import forms

from information.employment_info.models import Permisions, Personally
from .models import DailySchedule, Holidays, PersianCalender
from jalali_date.widgets import AdminJalaliDateWidget
from jalali_date.fields import JalaliDateField
from django_jalali.forms import jDateField
from django.db import connection


class HeaderForm(forms.Form):
    p_date = jDateField(widget=AdminJalaliDateWidget(attrs={'class': 'form-control'}),
        label="تاریخ",
        required=True)

#فرم مربوط به لوح شیفت
class HolidayForm(forms.ModelForm):
    date = jDateField(widget=AdminJalaliDateWidget, label="تاریخ")
    day = forms.CharField(label="روز", required=False)
    discription = forms.CharField(label="توضیحات", required=False)
    is_holiday = forms.BooleanField(initial=False, required=False)

    class Meta:
        model = DailySchedule
        fields = '__all__'
        widgets = {
            'date': AdminJalaliDateWidget,
        }
