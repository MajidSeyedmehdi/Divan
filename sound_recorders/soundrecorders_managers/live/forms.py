from django import forms
from django_jalali.forms import jDateField
from jalali_date.widgets import AdminJalaliDateWidget


class LiveDateFilterForm(forms.Form):
    start_date = jDateField(
        label="از تاریخ",
        required=False,
        widget=AdminJalaliDateWidget(attrs={"class": "form-control"}),
    )
    end_date = jDateField(
        label="تا تاریخ",
        required=False,
        widget=AdminJalaliDateWidget(attrs={"class": "form-control"}),
    )
