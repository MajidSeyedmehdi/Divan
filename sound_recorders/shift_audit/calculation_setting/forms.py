from django import forms
from django_jalali.forms import jDateField
from jalali_date.widgets import AdminJalaliDateWidget

class HeaderForm(forms.Form):
    start_date = jDateField(
        widget=AdminJalaliDateWidget(attrs={'class': 'form-control'}),
        required=False
    )

    end_date = jDateField(
        widget=AdminJalaliDateWidget(attrs={'class': 'form-control'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        default_start = kwargs.pop("default_start", None)
        default_end = kwargs.pop("default_end", None)

        super().__init__(*args, **kwargs)

        if default_start:
            self.fields['start_date'].initial = default_start
            self.fields['start_date'].disabled = True
        if default_end:
            self.fields['end_date'].initial = default_end
            self.fields['end_date'].disabled = True