from django import forms

from information.employment_info.models import Permisions
from .models import DailySchedule, SelectNetwork, PersianCalender,Network,Sound_Recorders,SelectSoundRecorder
from jalali_date.widgets import AdminJalaliDateWidget
from jalali_date.fields import JalaliDateField
from django_jalali.forms import jDateField
from django.db import connection



class HeaderForm1(forms.Form):
    p_date = jDateField(
        widget=AdminJalaliDateWidget(attrs={'class': 'form-control'}),
        label="تاریخ",
        required=True
    )
    # network = forms.ModelChoiceField(
    #     queryset=Network.objects.filter(active=True, is_active=True, del_field=False),
    #     label="شبکه",
    #     required=False,
    #     empty_label="انتخاب کنید",
    #
    # )
    # اضافه کردن گزینه "انتخاب کنید" و "همه"
    ALL_NETWORK = 'all'
    network = forms.ChoiceField(
        choices=[('', 'انتخاب کنید')] +  # گزینه "انتخاب کنید" به عنوان پیش‌فرض
                [(ALL_NETWORK, 'همه')] +  # گزینه "همه" اضافه می‌شود
                [(network.id_network, network.network) for network in Network.objects.filter(active=True, is_active=True, del_field=False)],
        label="شبکه",
        required=False,
        initial='',  # پیش‌فرض "انتخاب کنید" باشد
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

class HeaderForm(forms.Form):
    ALL_NETWORK = "all"
    ALL_RECORDER = "all_rec"

    p_date = jDateField(
        widget=AdminJalaliDateWidget(attrs={'class': 'form-control'}),
        label="تاریخ",
        required=True
    )
    network = forms.ChoiceField(
        label="شبکه",
        required=False
    )

    sound_recorder = forms.ChoiceField(
        label="صدابردار",
        required=False
    )

    shift_table_choice = forms.ChoiceField(
        label='انتخاب جدول شیفت',
        choices=[('1', 'لوح ابتدایی'), ('2', 'لوح برآورد')],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'min-width:150px; max-width:300px;'
        }),
        required=False
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ---- شبکه ----
        nets = [(str(n.id_network), n.network) for n in SelectNetwork.objects.all()]
        self.fields["network"].choices = [
            ("", "انتخاب کنید"),
            (self.ALL_NETWORK, "همه"),
        ] + nets

        # ---- صدابردار ----
        recs = [(str(r.id_sound_recorder), str(r)) for r in SelectSoundRecorder.objects.filter(id_personal__in=Permisions.objects.filter(permision_sound_recorders=True).values_list('id_personal_id',
                                                                                                  flat=True))]
        self.fields["sound_recorder"].choices = [
            ("", "انتخاب کنید"),
            (self.ALL_RECORDER, "همه"),
        ] + recs
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