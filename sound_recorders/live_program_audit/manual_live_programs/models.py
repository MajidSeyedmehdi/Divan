from django.db import models
import django_jalali.db.models as jmodels


class LiveDailySchedule(models.Model):
    date = models.DateField(unique=True, verbose_name="تاریخ")
    day = models.CharField(max_length=20, verbose_name="روز")

    def __str__(self):
        return f"{self.date}"

class LivePersianCalender(models.Model):
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

class Status(models.Model):
    id_live_status = models.IntegerField(primary_key=True, db_column='Id_live_status')
    status = models.CharField(max_length=100, db_column='Status')

    class Meta:
        managed = False
        db_table = 'Tbl_Live_Status'

    def __str__(self):
        return self.status  # مطمئن بشیم که نمایش فارسی درست ک

class ShiftNumber(models.Model):
    id_shift = models.IntegerField(primary_key=True, db_column='Id_shift')
    shift_number = models.CharField(max_length=100, db_column='Shift_number')

    class Meta:
        managed = False
        db_table = 'Tbl_Shift'

    def __str__(self):
        return str(self.shift_number) # مطمئن بشیم که نمایش فارسی درست ک

class NetworkShift(models.Model):
    id_network_shift = models.IntegerField(primary_key=True, db_column='Id_network_shift')
    id_network = models.IntegerField(db_column='Id_network')
    id_shift = models.IntegerField(db_column='Id_shift' )

    class Meta:
        managed = False
        db_table = 'Tbl_Network_Shift'

class Programs(models.Model):
    id_manual_program = models.IntegerField(primary_key=True, db_column='Id_manual_program')
    program_name = models.CharField(max_length=100, db_column='Program_name')

    class Meta:
        managed = False
        db_table = 'Tbl_Program_Sound_Spec'

