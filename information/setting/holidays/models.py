
from django.db import models
import django_jalali.db.models as jmodels

class DailySchedule(models.Model):
    date = models.DateField(unique=True, verbose_name="تاریخ")
    day = models.CharField(max_length=20, verbose_name="روز")

class PersianCalender(models.Model):
    title = models.CharField(max_length=255)
    p_date=jmodels.jDateField()

    def __str__(self):
        return f"{self.title} - {self.p_date}"

class Holidays(models.Model):
    id_holiday = models.IntegerField(primary_key=True, db_column='Id_holiday')
    discription = models.CharField(max_length=100, db_column='Description')

    class Meta:
        managed = False
        db_table = 'Tbl_Holidays'


