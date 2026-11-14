from django import forms
from django_jalali.forms import jDateField
from jalali_date.widgets import AdminJalaliDateWidget
from sound_recorders.models import Network
from sound_recorders.live_program_audit.live_financial_calculation.models import LiveStatus, LivePaymentStatus


class HeaderForm(forms.Form):

    program_name = forms.CharField(
        label='نام برنامه',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    start_date = jDateField(
        widget=AdminJalaliDateWidget(attrs={'class': 'form-control'}),
        required=False
    )

    end_date = jDateField(
        required=False,
        widget=AdminJalaliDateWidget(
            attrs={
                'class': 'form-control',
                'id': 'end_date'
            }
        )
    )

    network = forms.ModelChoiceField(
        queryset=Network.objects.filter(
            del_field=False,
            active=True,
            is_active=True
        ),
        label="انتخاب شبکه",
        empty_label="همه شبکه‌ها",
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        )
    )

    live_status = forms.ModelChoiceField(
        queryset=LiveStatus.objects.filter(
            active=True,
            del_field=False,
            # is_active=True
        ),
        label="وضعیت",
        empty_label="همه وضعیت‌ها",
        required=False,
        widget=forms.Select(
            attrs={
                'id': 'id_live_status', 'class': 'form-control'
            }
        )
    )

    live_payment_status = forms.ModelChoiceField(
        queryset=LivePaymentStatus.objects.filter(
            active=True,
            del_field=False,
        ),
        label="وضعیت پرداخت",
        empty_label="وضعیت پرداخت",
        required=False,  # چون در فیلتر ممکن است خالی باشد
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'id': 'id_payment_status'
            }
        )
    )


