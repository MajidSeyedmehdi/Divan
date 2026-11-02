import jdatetime
from django.db import models
from django.utils import timezone
from sound_recorders.models import Network


class TblProgramSpec(models.Model):
    id_program = models.AutoField(db_column='Id_program',primary_key=True)  # Field name made lowercase.
    program_name = models.CharField(db_column='Program_name', max_length=250, db_collation='Persian_100_CI_AS', blank=True, null=True)  # Field name made lowercase.
    code = models.CharField(db_column='Code', max_length=50, db_collation='Persian_100_CI_AS', blank=True, null=True)  # Field name made lowercase.
    id_network = models.ForeignKey(Network,db_column='Id_network',on_delete=models.CASCADE,null=False)  # Field name made lowercase.
    group_network = models.CharField(db_column='Group_network', max_length=50, db_collation='Persian_100_CI_AS', blank=True, null=True)  # Field name made lowercase.
    start_date = models.DateField(db_column='Start_date', blank=True, null=True)  # Field name made lowercase.
    end_date = models.DateField(db_column='End_date', blank=True, null=True)  # Field name made lowercase.
    permitted_count = models.IntegerField(db_column='Permitted_count', blank=True, null=True)  # Field name made lowercase.
    # used_count = models.IntegerField(db_column='Used_count', blank=True, null=True)
    time_duration = models.IntegerField(db_column='Time_duration', blank=True, null=True)  # Field name made lowercase.
    program_type = models.CharField(db_column='Program_type', max_length=50, db_collation='Persian_100_CI_AS', blank=True, null=True)  # Field name made lowercase.
    price_level0 = models.DecimalField(db_column='Price_level0', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    price_level1 = models.DecimalField(db_column='Price_level1', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    price_level2 = models.DecimalField(db_column='Price_level2', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    price_level3 = models.DecimalField(db_column='Price_level3', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    price_level4 = models.DecimalField(db_column='Price_level4', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    price_level5 = models.DecimalField(db_column='Price_level5', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    price_level6 = models.DecimalField(db_column='Price_level6', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    structure = models.CharField(db_column='Structure', max_length=50, db_collation='Persian_100_CI_AS', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=50, db_collation='Persian_100_CI_AS', blank=True, null=True)  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', blank=True, null=True)  # Field name made lowercase.
    del_field = models.BooleanField(db_column='Del', blank=True, null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    user_name = models.CharField(db_column='User_name', max_length=50, db_collation='Persian_100_CI_AS', blank=True, null=True)  # Field name made lowercase.
    update_date = models.DateTimeField(db_column='Update_date',default=timezone.now, blank=True, null=True)  # Field name made lowercase.

    @property
    def start_date_jalali(self):
        if self.start_date:
            return jdatetime.date.fromgregorian(date=self.start_date).strftime('%Y/%m/%d')
        return '-'

    @property
    def end_date_jalali(self):
        if self.end_date:
            return jdatetime.date.fromgregorian(date=self.end_date).strftime('%Y/%m/%d')
        return '-'

    class Meta:
        managed = False
        db_table = 'Tbl_Program_Spec'
