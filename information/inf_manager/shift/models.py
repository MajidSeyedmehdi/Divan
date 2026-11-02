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


class Leaves(models.Model):
    id_leave = models.CharField(max_length=100, db_column='Id_leave')
    leaves = models.CharField(max_length=100, db_column='Leaves')

    class Meta:
        managed = False
        db_table = 'Tbl_Leaves'

class Mandatory_Hours(models.Model):
    id_mandatory_hours = models.CharField(max_length=100, db_column='Id_mandatory_hours')
    mandatory_hours = models.CharField(max_length=100, db_column='Mandatory_hours')

    class Meta:
        managed = False
        db_table = 'Tbl_Mandatory_Hours'

class Job_Relation(models.Model):
    id_job_relation = models.CharField(max_length=100, db_column='Id_job_relation')
    job_relation = models.CharField(max_length=100, db_column='Job_relation')

    class Meta:
        managed = False
        db_table = 'Tbl_Job_Relation'

class Hire_Status(models.Model):
    id_hire_status = models.CharField(max_length=100, db_column='Id_hire_status')
    hire_status = models.CharField(max_length=100, db_column='Hire_status')

    class Meta:
        managed = False
        db_table = 'Tbl_Hire_Status'

class Payment_Type(models.Model):
    id_payment_type = models.CharField(max_length=100, db_column='Id_payment_type')
    payment_type = models.CharField(max_length=100, db_column='Payment_type')

    class Meta:
        managed = False
        db_table = 'Tbl_Payment_Type'

class Manager(models.Model):
    id_manager = models.CharField(max_length=100, db_column='Id_manager')
    manager = models.CharField(max_length=100, db_column='Manager')

    class Meta:
        managed = False
        db_table = 'Tbl_Manager'