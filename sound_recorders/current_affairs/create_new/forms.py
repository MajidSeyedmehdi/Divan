from django import forms
from .models import DailySchedule, SelectNetwork, PersianCalender,Network,Sound_Recorders,SelectSoundRecorder
from jalali_date.widgets import AdminJalaliDateWidget
from jalali_date.fields import JalaliDateField
from django_jalali.forms import jDateField
from django.db import connection


class HeaderForm(forms.Form):
    p_date = jDateField(widget=AdminJalaliDateWidget(attrs={'class': 'form-control'}),
        label="تاریخ",
        required=True)
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
#برای تقویم فارسی
# class PersianCalenderForm(forms.ModelForm):
#     p_date = jDateField(widget=AdminJalaliDateWidget, label="تاریخ")
#
#     class Meta:
#         model = PersianCalender
#         fields = ['p_date', 'title']


class SoundShiftAssignmentForm:
    """
    Form class for handling initial sound shift assignment using stored procedure
    """
    
    @staticmethod
    def save_initial_assignment(user, sound_recorder_id, shift_id, network_id, shift_date, shift_day):
        """
        Save initial sound shift assignment using stored procedure
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                EXEC Sp_InsertSoundShiftAssignment
                    @id_sound_recorder=%s, @id_shift=%s, @id_network=%s, 
                    @shift_date=%s, @shift_day=%s, @user_name=%s
            """, [
                sound_recorder_id,
                shift_id,
                network_id,
                shift_date,
                shift_day,
                user.username
            ])
            
            result = cursor.fetchone()
            
            if result and (('ErrorMessage' in result) or (isinstance(result, dict) and result.get('ErrorMessage')) or (isinstance(result, tuple) and any('Error' in str(x) for x in result if x))):
                raise forms.ValidationError(result)
            
            return result

    @staticmethod
    def fetch_assignments_by_month(network_id: int, year: int, month: int):
        """
        Fetch existing assignments for a given network and Gregorian year/month via SP.
        Returns a list of dict rows: [{shift_date, id_shift, id_sound_recorder}, ...]
        """
        rows = []
        with connection.cursor() as cursor:
            cursor.execute(
                """
                EXEC Sp_GetSoundShiftAssignmentsByMonth
                    @id_network=%s, @year=%s, @month=%s
                """,
                [network_id, year, month],
            )
            columns = [col[0] for col in cursor.description] if cursor.description else []
            for db_row in cursor.fetchall() if cursor.description else []:
                row = dict(zip(columns, db_row))
                rows.append(row)
        return rows

