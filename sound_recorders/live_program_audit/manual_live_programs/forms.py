from django import forms
from sound_recorders.current_affairs.create_new.models import SelectSoundRecorder
from information.employment_info.models import Permisions
from .models import LiveDailySchedule, SelectNetwork, Status, ShiftNumber, NetworkShift
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
        label="شبکه",
        queryset=SelectNetwork.objects.all(),
        required=False,
        empty_label="انتخاب شبکه",
        widget=forms.Select(attrs={'id': 'id_network', 'class': 'form-control'})
    )
    day = forms.CharField(
        label="روز",
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'id_day', 'readonly': 'readonly'}
        )
    )
    shift_number = forms.ModelChoiceField(
        label="شیفت",
        queryset=ShiftNumber.objects.none(),
        required=False,
        empty_label="انتخاب شیفت",
        widget=forms.Select(attrs={'id': 'id_shift_number', 'class': 'form-control'})
    )
    status = forms.ModelChoiceField(
        label="وضعیت",
        queryset=Status.objects.all(),
        required=False,  # الزامی شود تا کاربر نتواند خالی بفرستد
        empty_label=None,  # حذف گزینه "انتخاب وضعیت"
        initial=1,  # انتخاب پیش‌فرض روی مقدار 1 (یا شیء مربوط به آن)
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sound_recorder = forms.ModelChoiceField(
        queryset=SelectSoundRecorder.objects.filter(
            id_personal__in=Permisions.objects.filter(permision_sound_recorders=True).values_list('id_personal_id',
                                                                                                  flat=True)).order_by(
            'id_personal__last_name', 'id_personal__first_name'),
        label="صدابردار",
        required=False,
        empty_label="انتخاب کنید"
    )

    def __init__(self, *args, **kwargs):
        default_start = kwargs.pop("default_start", None)
        super().__init__(*args, **kwargs)

        # پشتیبانی از فرم ارسال شده (POST یا GET)
        network_id = self.data.get('network')

        if network_id:
            try:
                network_id = int(network_id)
                shift_ids = NetworkShift.objects.filter(
                    id_network=network_id
                ).values_list('id_shift', flat=True)

                self.fields['shift_number'].queryset = ShiftNumber.objects.filter(
                    id_shift__in=shift_ids
                )
            except (ValueError, TypeError):
                pass

        if default_start:
            self.fields['start_date'].initial = default_start
            self.fields['day'].initial = self.get_persian_day(default_start)

    @staticmethod
    def get_persian_day(date):
        days = {
            0: "شنبه", 1: "یکشنبه", 2: "دوشنبه",
            3: "سه‌شنبه", 4: "چهارشنبه", 5: "پنجشنبه", 6: "جمعه",
        }
        return days[date.weekday()]

