from django.db import models
from django.forms import IntegerField
from django.utils import timezone
from information.employment_info.models import Personally,Official,Levels,JobUnit,JobTitle,JobRelation,CurrentJob,HireStatus



# Create your models here.
class Network(models.Model):
    id_network = models.AutoField(db_column='Id_network',primary_key=True)
    network = models.CharField(db_column='Network',max_length=50,db_collation='Persian_100_CI_AS',null=False)
    is_active = models.BooleanField(db_column='Is_active',default=True , null=False)
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now,null=False)
    class Meta:
        managed = False
        db_table = 'Tbl_Network'
    def __str__(self):
        return self.network  # یا هر فیلدی که می‌خوای در سلکت‌باکس نمایش داده بشه

class Shift_Type(models.Model):
    id_shift_type = models.AutoField(db_column='Id_shift_type',primary_key=True)
    Shift_type = models.IntegerField(db_column='Shift_type',null=False)
    shift_type_name = models.CharField(db_column='Shift_type_name',max_length=50,null=False)
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now, null=False)
    class Meta:
        managed = False
        db_table = 'Tbl_Shift_Type'
    # id_shift_type = models.AutoField(db_column='Id_shift_type',primary_key=True)
    # shift_type = models.IntegerField(db_column='Shift_type',null=False)
    # active = models.BooleanField(db_column='Active', default=True, null=False)
    # del_field = models.BooleanField(db_column='Del', default=False, null=False)
    # update_date = models.DateTimeField(db_column='Update_date', default=timezone.now,null=False)
    # class Meta:
    #     managed = False
    #     db_table = 'Tbl_Shift_Type'


class Shift(models.Model):
    id_shift = models.AutoField(db_column='Id_shift',primary_key=True)
    id_shift_type = models.ForeignKey(Shift_Type,db_column='Id_shift_type',on_delete=models.CASCADE,null=False)
    shift_name = models.CharField(db_column='Shift_name',max_length=50,db_collation='Persian_100_CI_AS',null=True)
    shift_time = models.CharField(db_column='Shift_time',max_length=50,null=True)
    shift_number = models.IntegerField(db_column='Shift_number',null=False)
    start_time = models.TimeField(db_column='Start_time',null=False)
    end_time = models.TimeField(db_column='End_time', null=False)
    is_active = models.BooleanField(db_column='Is_active',default=True , null=False)
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now,null=False)
    class Meta:
        managed = False
        db_table = 'Tbl_Shift'

class Network_Settings(models.Model):
    id_network_settings = models.AutoField(db_column='Id_network_settings',primary_key=True)
    id_network = models.ForeignKey(Network,db_column='Id_network',on_delete=models.CASCADE,null=False)
    shift_count = models.IntegerField(db_column='Shift_count',null=False)
    live_count = models.IntegerField(db_column='Live_count',null=False)
    coefficient = models.FloatField(db_column='Coefficient',null=False,default=1)
    has_live = models.BooleanField(db_column='Has_live', default=True, null=False)
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now, null=False)
    class Meta:
        managed = False
        db_table = 'Tbl_Network_Settings'

class Network_Shift(models.Model):
    id_network_shift = models.AutoField(db_column='Id_network_shift',primary_key=True)
    id_network = models.ForeignKey(Network,db_column='Id_network',on_delete=models.CASCADE,null=False)
    id_shift = models.ForeignKey(Shift,db_column='Id_shift',on_delete=models.CASCADE,null=False)
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now, null=False)
    class Meta:
        managed = False
        db_table = 'Tbl_Network_Shift'

class Shift_Rate(models.Model):
    id_shift_rate = models.AutoField(db_column='Id_shift_rate',primary_key=True)
    id_shift_type = models.ForeignKey(Shift_Type,db_column='Id_shift_type',on_delete=models.CASCADE,null=False)
    shift_number = models.IntegerField(db_column='Shift_number',null=True)
    id_current_job = models.ForeignKey(CurrentJob, db_column='Id_current_job', on_delete=models.CASCADE, null=False)
    id_levels = models.ForeignKey(Levels, db_column='Id_levels', on_delete=models.CASCADE, null=False)
    shift_rate = models.DecimalField(db_column='Shift_rate',max_digits=18,decimal_places=0,null=False,default=0)
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now, null=False)
    user_name = models.CharField(db_column='User_name',max_length=50,null=True)

    class Meta:
        managed = False
        db_table = 'Tbl_Shift_Rate'


class Holidays(models.Model):
    id_holiday = models.AutoField(db_column='Id_holiday',primary_key=True)
    holiday_date = models.CharField(db_column='Holiday_date',max_length=10,null=False)
    shamsi_date = models.CharField(db_column='Shamsi_date',max_length=10,null=False)
    holiday_type = models.CharField(db_column='Holiday_type',max_length=100,null=True)
    Description = models.TextField(db_column='Description',null=False)
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now, null=False)
    class Meta:
        managed = False
        db_table = 'Tbl_Holidays'
class Rate_Rules(models.Model):
    id_rules = models.AutoField(db_column='Id_rules',primary_key=True)
    id_network = models.ForeignKey(Network,db_column='Id_network',on_delete=models.CASCADE,null=False)
    id_shift = models.ForeignKey(Shift,db_column='Id_shift',on_delete=models.CASCADE,null=False)
    id_shift_type = models.ForeignKey(Shift_Type,db_column='Id_shift_type',on_delete=models.CASCADE,null=False)
    shamsi_date = models.CharField(db_column='Shamsi_date',max_length=10,null=False)
    shift_name = models.CharField(db_column='Shift_name',max_length=50,null=False)
    is_holiday = models.BooleanField(db_column='Is_holiday', default=False, null=False)
    final_rate = models.DecimalField(max_digits=10, decimal_places=2, db_column='Rate_Multiplier', null=False , blank=False)
    rule_date = models.CharField(db_column='Rate_date',max_length=10,null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now, null=False)
    class Meta:
        managed = False
        db_table = 'Tbl_Rate_Rules'

class Sound_Recorders(models.Model):
    id_sound_recorder = models.AutoField(db_column='Id_sound_recorder',primary_key=True)
    id_personal = models.ForeignKey(Personally, db_column='Id_personal', on_delete=models.CASCADE, null=False)
    id_official = models.ForeignKey(Official, db_column='Id_official', on_delete=models.CASCADE, null=False)
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now, null=False)

    class Meta:
        managed = False
        db_table = 'Tbl_Sound_Recorders'


class SoundShiftAssignment(models.Model):
    id_sound_shift = models.AutoField(db_column='Id_sound_shift',primary_key=True)
    id_sound_recorder = models.ForeignKey(Sound_Recorders,db_column='Id_sound_recorder',on_delete=models.CASCADE, null=False)
    id_shift = models.ForeignKey(Shift,db_column='Id_shift',on_delete=models.CASCADE)
    id_network = models.ForeignKey(Network,db_column='Id_network',on_delete=models.CASCADE, null=False)
    shift_date = models.DateField(db_column='Shift_date',null=False)
    lock = models.BooleanField(db_column='Lock', default=False, null=True)
    shift_day = models.CharField(db_column='Shift_day',max_length=50,null=False)
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now, null=False)

    class Meta:
        managed = False
        db_table = 'Tbl_Sound_Shift_Assignment'

class SoundShifFinal(models.Model):
    id_sound_shift_final = models.AutoField(db_column='Id_sound_shift_final',primary_key=True)
    id_sound_recorder = models.ForeignKey(Sound_Recorders,db_column='Id_sound_recorder',on_delete=models.CASCADE, null=False)
    id_shift = models.ForeignKey(Shift,db_column='Id_shift',on_delete=models.CASCADE)
    id_network = models.ForeignKey(Network,db_column='Id_network',on_delete=models.CASCADE, null=False)
    shift_date = models.DateField(db_column='Shift_date',null=False)
    shift_day = models.CharField(db_column='Shift_day',max_length=50,null=False)
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now, null=False)

    class Meta:
        managed = False
        db_table = 'Tbl_Sound_Shift_Final'

class MiddlewareShift(models.Model):
    id = models.AutoField(db_column='Id',primary_key=True)
    base_shift = models.IntegerField(db_column='Base_shift',null=False)
    join_shift = models.IntegerField(db_column='Join_shift',null=False)
    class Meta:
        managed = False
        db_table = 'Tbl_Middleware_Shift'

# class Shift_Types(models.Model):

class Shift_Payroll_Calc(models.Model):
    id_calc = models.AutoField(db_column='Id_calc',primary_key=True)
    id_sound_shift_final = models.ForeignKey(SoundShifFinal,db_column='Id_sound_shift_final',on_delete=models.CASCADE,null=False)
    shift_date = models.CharField(db_column='Shift_date',max_length=10,null=False)
    id_network = models.ForeignKey(Network,db_column='Id_network',on_delete=models.CASCADE, null=False)
    id_shift = models.ForeignKey(Shift,db_column='Id_shift',on_delete=models.CASCADE, null=False)
    id_shift_type = models.ForeignKey(Shift_Type,db_column='Id_shift_type',on_delete=models.CASCADE, null=False)
    id_sound_recorder = models.ForeignKey(Sound_Recorders,db_column='Id_sound_recorder',on_delete=models.CASCADE, null=False)
    id_current_job = models.ForeignKey(CurrentJob,db_column='Id_current_job',on_delete=models.CASCADE, null=False)
    rule_date =  models.CharField(db_column='Rule_date',max_length=10,null=False)
    is_holiday = models.BooleanField(db_column='IsHoliday', default=False, null=False)
    final_rule_rate = models.DecimalField(db_column='Final_rule_rate',max_digits=5,decimal_places=2,null=False)
    shift_base_rate = models.DecimalField(db_column='Shift_base_rate',max_digits=5,decimal_places=2,null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now, null=False)
    user_name = models.CharField(db_column='User_name', max_length=50, null=False)
    class Meta:
        managed = False
        db_table = 'Tbl_Shift_Payroll_Calc'



class Job_Levels (models.Model):
    id_job_level = models.AutoField(db_column='Id_job_level',primary_key=True)
    current_job_id = models.ForeignKey(CurrentJob,db_column='Current_job_id',on_delete=models.CASCADE, null=False)
    level_id = models.ForeignKey(Levels,db_column='Level_id',on_delete=models.CASCADE, null=False)
    Active = models.BooleanField(db_column='Active', default=True, null=False)
    Del_field = models.BooleanField(db_column='Del', default=False, null=False)
    class Meta:
        managed = False
        db_table = 'Tbl_Job_Levels'