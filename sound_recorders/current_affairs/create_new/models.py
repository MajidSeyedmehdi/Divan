from django.db import models
import django_jalali.db.models as jmodels
from sound_recorders.models import Network,Network_Settings,SoundShiftAssignment,Sound_Recorders,Shift,Shift_Type,Network_Shift
from information.employment_info.models import Personally,Official,Levels
from django.utils import timezone
class DailySchedule(models.Model):
    date = models.DateField(unique=True, verbose_name="تاریخ")
    day = models.CharField(max_length=20, verbose_name="روز")
    shift = models.CharField(max_length=255, verbose_name="شیفت")

    def __str__(self):
        return f"{self.date} - {self.shift}"

class PersianCalender(models.Model):
    title = models.CharField(max_length=255)
    p_date=jmodels.jDateField()

    def __str__(self):
        return f"{self.title} - {self.p_date}"

class SelectNetwork(models.Model):
    id_network = models.IntegerField(primary_key=True, db_column='Id_network')
    network = models.CharField(max_length=100, db_column='Network')

    class Meta:
        managed = False
        db_table = 'Tbl_Network'


    def __str__(self):
        return self.network  # مطمئن بشیم که نمایش فارسی درست ک

class SelectSoundRecorder(models.Model):
    id_sound_recorder = models.IntegerField(primary_key=True, db_column='Id_sound_recorder')
    id_personal = models.ForeignKey(Personally,db_column='Id_personal',on_delete=models.CASCADE)


    class Meta:
        managed = False
        db_table = 'Tbl_Sound_Recorders'
    def __str__(self):
        return f"{self.id_personal.first_name}  {self.id_personal.last_name}"

