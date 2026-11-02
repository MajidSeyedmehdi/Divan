from django.db import models
import django_jalali.db.models as jmodels

class DailySchedule(models.Model):
    date = models.DateField(unique=True, verbose_name="تاریخ")

class PersianCalender(models.Model):
    title = models.CharField(max_length=255)
    p_date=jmodels.jDateField()

    def __str__(self):
        return f"{self.title} - {self.p_date}"
