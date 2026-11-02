from django.db import models
from django.utils import timezone
#
# from sound_recorders.models import Shift_Types
# from information.employment_info.models import CurrentJob,Levels
# class ShiftRate(models.Model):
#     id_shift_rate = models.IntegerField(db_column='Id_shift_rate',primary_key=True)
#     id_shift_type = models.ForeignKey(Shift_Types,db_column='Id_shift_type',on_delete=models.CASCADE)
#     id_current_job = models.ForeignKey(CurrentJob,db_column='Id_current_job',on_delete=models.CASCADE)
#     id_levels = models.ForeignKey(Levels, db_column='Id_levels', on_delete=models.CASCADE)
#     shift_rate = models.DecimalField(db_column='Shift_rate',max_digits=18,decimal_places=0)
#     active = models.BooleanField(db_column='Active', default=True, null=False)
#     del_field = models.BooleanField(db_column='Del', default=False, null=False)
#     update_date = models.DateTimeField(db_column='Update_date', default=timezone.now, null=False)
#     user_name = models.CharField(db_column='User_name',max_length=50,null=False)
#
#     class Meta:
#         managed = False
#         db_table = 'Tbl_Shift_Rate'
#
# class SelectShiftType(models.Model):
#     id_shift_type = models.IntegerField(db_column='Id_shift_type',primary_key=True)
#     shift_type_name = models.CharField(db_column='Shift_type_name',max_length=50,null=False)
#
#     class Meta:
#         managed = False
#         db_table = 'Tbl_Shift_type'
class Shift_Types(models.Model):
    id_shift_type = models.AutoField(primary_key=True, db_column='Id_shift_type')
    shift_type_name = models.CharField(max_length=50, db_column='Shift_type_name')
    active = models.BooleanField(db_column='Active', default=True)
    del_field = models.BooleanField(db_column='Del', default=False)

    class Meta:
        managed = False
        db_table = 'Tbl_Shift_Type'
        verbose_name = 'نوع شیفت'
        verbose_name_plural = 'انواع شیفت'

    def __str__(self):
        return self.shift_type_name


class CurrentJob(models.Model):
    id_current_job = models.AutoField(primary_key=True, db_column='Id_current_job')
    current_job = models.CharField(max_length=100, db_column='Current_job')
    active = models.BooleanField(db_column='Active', default=True)
    del_field = models.BooleanField(db_column='Del', default=False)
    is_seda = models.BooleanField(db_column='Is_seda', default=False)

    class Meta:
        managed = False
        db_table = 'Tbl_Current_Job'
        verbose_name = 'شغل فعلی'
        verbose_name_plural = 'شغل‌های فعلی'

    def __str__(self):
        return self.current_job


class Levels(models.Model):
    id_levels = models.AutoField(primary_key=True, db_column='Id_levels')
    levels = models.CharField(max_length=100, db_column='Levels')
    order = models.IntegerField(db_column='Order')
    active = models.BooleanField(db_column='Active', default=True)
    del_field = models.BooleanField(db_column='Del', default=False)

    class Meta:
        managed = False
        db_table = 'Tbl_Levels'
        verbose_name = 'رده شغلی'
        verbose_name_plural = 'رده‌های شغلی'
        ordering = ['order']

    def __str__(self):
        return self.levels


class Shift(models.Model):
    id_shift = models.AutoField(primary_key=True, db_column='Id_shift')
    shift_number = models.IntegerField(db_column='Shift_number')
    id_shift_type = models.ForeignKey(Shift_Types, db_column='Id_shift_type', on_delete=models.CASCADE)
    shift_name = models.CharField(max_length=50, db_column='Shift_name')

    class Meta:
        managed = False
        db_table = 'Tbl_Shift'
        verbose_name = 'شیفت'
        verbose_name_plural = 'شیفت‌ها'

    def __str__(self):
        return f"{self.id_shift_type.shift_type_name} - شیفت {self.shift_name}"


class ShiftRate(models.Model):
    id_shift_rate = models.IntegerField(db_column='Id_shift_rate', primary_key=True)
    id_shift_type = models.ForeignKey(Shift_Types, db_column='Id_shift_type', on_delete=models.CASCADE)
    shift_name = models.CharField(max_length=50, db_column='Shift_name')
    id_current_job = models.ForeignKey(CurrentJob, db_column='Id_current_job', on_delete=models.CASCADE)
    id_levels = models.ForeignKey(Levels, db_column='Id_levels', on_delete=models.CASCADE)
    shift_rate = models.DecimalField(max_digits=10, decimal_places=2, db_column='Shift_rate')
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now, null=False)
    user_name = models.CharField(db_column='User_name', max_length=50, null=False)

    class Meta:
        managed = False
        db_table = 'Tbl_Shift_Rate'
        verbose_name = 'نرخ شیفت'
        verbose_name_plural = 'نرخ‌های شیفت'

    def __str__(self):
        return f"{self.id_current_job.current_job} - {self.id_levels.levels} - {self.id_shift_type.shift_type_name}"


# مدل برای ویو (برای فیلتر کردن)
class VShiftLevelJob(models.Model):
    shift_type_name = models.CharField(max_length=100)
    shift_number = models.IntegerField()
    id_shift_type = models.IntegerField()
    id_levels = models.IntegerField()
    levels = models.CharField(max_length=100)
    level_order = models.IntegerField()
    id_current_job = models.IntegerField()
    current_job = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'V_Shift_Level_Job'

    def __str__(self):
        return f"{self.current_job} - {self.levels}"


