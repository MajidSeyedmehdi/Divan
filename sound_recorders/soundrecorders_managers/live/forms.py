# from django import forms
# from django_jalali.forms import jDateField
# from jalali_date.widgets import AdminJalaliDateWidget
#
#
# class LiveDateFilterForm(forms.Form):
#     start_date = jDateField(
#         label="از تاریخ",
#         required=False,
#         widget=AdminJalaliDateWidget(attrs={"class": "form-control"}),
#     )
#     end_date = jDateField(
#         label="تا تاریخ",
#         required=False,
#         widget=AdminJalaliDateWidget(attrs={"class": "form-control"}),
#     )
from django import forms
from sound_recorders.current_affairs.create_new.models import SelectSoundRecorder
from information.employment_info.models import Permisions
from sound_recorders.live_program_audit.manual_live_programs.models import SelectNetwork, Status
from sound_recorders.live_program_audit.live_financial_calculation.models import LivePaymentStatus
from jalali_date.widgets import AdminJalaliDateWidget
from jalali_date.fields import JalaliDateField
from django_jalali.forms import jDateField
from django.db import connection


class HeaderForm(forms.Form):
    program_name = forms.CharField(
        label='نام برنامه',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    start_date = jDateField(
        widget=AdminJalaliDateWidget(attrs={'class': 'form-control'}),
        required=True
    )
    end_date = jDateField(
        required=True,
        widget=AdminJalaliDateWidget(
            attrs={
                'class': 'form-control',
                'id': 'end_date'
            }
        )
    )
    network = forms.ModelChoiceField(
        label="شبکه",
        queryset=SelectNetwork.objects.all(),
        required=False,
        empty_label="همه شبکه‌ها",
        widget=forms.Select(attrs={'id': 'id_network', 'class': 'form-control'})
    )

    status = forms.ModelChoiceField(
        label="وضعیت",
        queryset=Status.objects.all(),
        required=False,  # الزامی شود تا کاربر نتواند خالی بفرستد
        empty_label=None,  # حذف گزینه "انتخاب وضعیت"
        initial=2,  # انتخاب پیش‌فرض روی مقدار 1 (یا شیء مربوط به آن)
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    payment_status = forms.ModelChoiceField(
        label="وضعیت پرداخت",
        queryset=LivePaymentStatus.objects.all(),
        required=False,
        empty_label="همه وضعیت‌ها",
        initial=2,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_payment_status'
        })
    )

    def __init__(self, *args, **kwargs):
        default_start = kwargs.pop("default_start", None)
        super().__init__(*args, **kwargs)

        if default_start:
            self.fields['start_date'].initial = default_start




