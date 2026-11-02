from django.db import models
import django_jalali.db.models as jmodels
from sound_recorders.models import Network,Network_Settings,SoundShiftAssignment,Sound_Recorders,Shift,Shift_Type,Network_Shift
from information.employment_info.models import Personally,Official,Levels
from django.utils import timezone
class DailySchedule(models.Model):
    date = models.DateField(unique=True, verbose_name="تاریخ")

class PersianCalender(models.Model):
    title = models.CharField(max_length=255)
    p_date=jmodels.jDateField()

    def __str__(self):
        return f"{self.title} - {self.p_date}"

