from django import forms
from .models import DailySchedule, SelectNetwork, PersianCalender,Network,Sound_Recorders,SelectSoundRecorder
from jalali_date.widgets import AdminJalaliDateWidget
from jalali_date.fields import JalaliDateField
from django_jalali.forms import jDateField
from django.db import connection



class HeaderForm(forms.Form):
    p_date = jDateField(
        widget=AdminJalaliDateWidget(attrs={'class': 'form-control'}),
        label="تاریخ",
        required=True
    )
    network = forms.ModelChoiceField(
        queryset=Network.objects.filter(active=True, is_active=True, del_field=False),
        label="شبکه",
        required=False,
        empty_label="انتخاب کنید"
    )
    sound_recorder = forms.ModelChoiceField(
        queryset=SelectSoundRecorder.objects.all(),
        label="صدابردار",
        required=False,
        empty_label="انتخاب کنید"
    )
    shift_table_choice = forms.ChoiceField(
        label='جدول شیفت',
        choices=[('1', 'لوح ابتدایی'), ('2', 'لوح برآورد')],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'min-width:150px; max-width:300px;'
        }),
        required=False
    )
    # network = forms.ChoiceField(label='شبکه', required=False)
    #
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     networks = SelectNetwork.objects.values_list('network', 'network').distinct()
    #     self.fields['network'].choices = [('', 'انتخاب کنید')] + list(networks)

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