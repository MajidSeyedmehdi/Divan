from django import forms
from django.db.models import Q
from information.employment_info.models import Permisions, Personally
from .models import DailySchedule, SelectNetwork, PersianCalender,Network,Sound_Recorders,SelectSoundRecorder
from jalali_date.widgets import AdminJalaliDateWidget
from jalali_date.fields import JalaliDateField
from django_jalali.forms import jDateField
from django.db import connection


class HeaderForm(forms.Form):
    p_date = jDateField(widget=AdminJalaliDateWidget(attrs={'class': 'form-control'}),
        label="تاریخ",
        required=True)

    # تاریخ مستقل برای جابه‌جایی شبکه
    swap_shift_date = jDateField(
        widget=AdminJalaliDateWidget(attrs={'class': 'form-control'}),
        label="تاریخ جابه‌جایی",
        required=False
    )
    network = forms.ModelChoiceField(
        queryset=Network.objects.filter(active=True, is_active=True, del_field=False),
        label="شبکه",
        required=False,
        empty_label="همه شبکه‌ها"
    )

    # تاریخ مستقل برای جابه‌جایی بین شبکه‌ها
    swap_date = jDateField(
        widget=AdminJalaliDateWidget(attrs={'class': 'form-control'}),
        label="تاریخ جابه‌جایی",
        required=False
    )

    # sound_recorder = forms.ModelChoiceField(
    #     queryset=SelectSoundRecorder.objects.all(),
    #     label="صدابردار",
    #     required=False,
    #     empty_label="انتخاب کنید"
    # )
    sound_recorder = forms.ModelChoiceField(
        queryset=SelectSoundRecorder.objects.filter(
            id_personal__in=Permisions.objects.filter(Q(permision_sound_recorders=True) | Q(permision_assistant_sound_recorder=True)).values_list('id_personal_id',
                           flat=True)).filter(active=True,del_field=False).order_by('id_personal__last_name', 'id_personal__first_name'),

        label="صدابردار",
        required=False,
        empty_label="انتخاب کنید"
    )


#فرم مربوط به لوح شیفت
class DailyScheduleForm(forms.ModelForm):
    date = jDateField(widget=AdminJalaliDateWidget, label="تاریخ")
    day = forms.CharField(label="روز", required=False)
    shift = forms.CharField(widget=forms.HiddenInput(), required=False)  # برای نگهداری مقادیر سلول‌ها

    class Meta:
        model = DailySchedule
        fields = '__all__'
        widgets = {
            'date': AdminJalaliDateWidget,
        }
