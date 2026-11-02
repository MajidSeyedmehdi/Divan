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

    permanent_personel = forms.CharField(label='پرسنل موظف', required=False)
    support_personel = forms.CharField(label='پرسنل کمکی', required=False)
    leaves = forms.CharField(label=' مرخصی', required=False)
    mandatory_hours = forms.CharField(label='ساعت موظف', required=False)
    amrie = forms.CharField(label=' امریه', required=False)
    extra_payment = forms.ChoiceField(label='اضافه کار', required=False)
    payment_type = forms.CharField(label='نوع پرداخت', required=False)
    manager = forms.CharField(label='مدیریت', required=False)


    def __init__(self, *args, **kwargs):
        default_start = kwargs.pop("default_start", None)
        default_end = kwargs.pop("default_end", None)

        super().__init__(*args, **kwargs)

        if default_start:
            self.fields['start_date'].initial = default_start

        if default_end:
            self.fields['end_date'].initial = default_end
