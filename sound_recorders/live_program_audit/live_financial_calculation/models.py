import jdatetime
from django.db import models
from django.utils import timezone
from sound_recorders.models import Sound_Recorders
from sound_recorders.shift_audit.financial_report.models import Manager
class SoundShiftLive(models.Model):
    id_sound_shift_live = models.AutoField(db_column='Id_sound_shift_live', primary_key=True)  # Field name made lowercase.
    id_manual_program = models.IntegerField(db_column='Id_manual_program', blank=True, null=True)  # Field name made lowercase.
    id_sound_recorder = models.ForeignKey('Sound_Recorders', models.DO_NOTHING, db_column='Id_sound_recorder', blank=True, null=True)  # Field name made lowercase.
    live_shift_date = models.DateField(db_column='Live_shift_date', blank=True, null=True)  # Field name made lowercase.
    live_shift_day = models.CharField(db_column='Live_shift_day', max_length=50, db_collation='Persian_100_CI_AS', blank=True, null=True)  # Field name made lowercase.
    id_manager = models.ForeignKey('Manager', models.DO_NOTHING, db_column='Id_manager', blank=True, null=True)  # Field name made lowercase.
    id_payment_status = models.IntegerField(db_column='Id_payment_status', blank=True, null=True)  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', blank=True, null=True)  # Field name made lowercase.
    del_field = models.BooleanField(db_column='Del', blank=True, null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    update_date = models.DateTimeField(db_column='Update_date', blank=True, null=True)  # Field name made lowercase.
    user_name = models.CharField(db_column='User_name', max_length=50, db_collation='Persian_100_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_Sound_Shift_Live'


class LivePaymentStatus(models.Model):
    id_live_payment_status = models.AutoField(db_column='Id_live_payment_status', primary_key=True)  # Field name made lowercase.
    live_payment_status = models.CharField(db_column='Live_payment_status', max_length=50, db_collation='Persian_100_CI_AS', blank=True, null=True)  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', blank=True, null=True)  # Field name made lowercase.
    del_field = models.BooleanField(db_column='Del', blank=True, null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    update_date = models.DateTimeField(db_column='Update_date', blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.live_payment_status if self.live_payment_status else ""
    class Meta:
        managed = False
        db_table = 'Tbl_Live_Payment_Status'


class LiveRateRules(models.Model):
    id_live_rate_rule = models.OneToOneField('self', models.DO_NOTHING, db_column='Id_live_rate_rule', primary_key=True)  # Field name made lowercase.
    id_job_title = models.IntegerField(db_column='Id_job_title', blank=True, null=True)  # Field name made lowercase.
    live_rate_rule = models.DecimalField(db_column='Live_rate_rule', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', blank=True, null=True)  # Field name made lowercase.
    del_field = models.BooleanField(db_column='Del', blank=True, null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    update_date = models.DateTimeField(db_column='Update_date', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_Live_Rate_Rules'


class LiveWorkflowHistory(models.Model):
    id_live_workflow = models.AutoField(db_column='Id_live_workflow', primary_key=True)  # Field name made lowercase.
    id_sound_shift_live = models.IntegerField(db_column='Id_sound_shift_live', blank=True, null=True)  # Field name made lowercase.
    id_manager = models.IntegerField(db_column='Id_manager', blank=True, null=True)  # Field name made lowercase.
    workflow_action = models.CharField(db_column='Workflow_action', max_length=50, db_collation='Persian_100_CI_AS', blank=True, null=True)  # Field name made lowercase.
    action_date = models.DateTimeField(db_column='Action_Date', blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=50, db_collation='Persian_100_CI_AS', blank=True, null=True)  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', blank=True, null=True)  # Field name made lowercase.
    del_field = models.BooleanField(db_column='Del', blank=True, null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    user_name = models.CharField(db_column='User_name', max_length=50, db_collation='Persian_100_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_Live_Workflow_History'


class LiveStatus(models.Model):
    id_live_status = models.AutoField(db_column='Id_live_status', primary_key=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50, db_collation='Persian_100_CI_AS', blank=True, null=True)  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', blank=True, null=True)  # Field name made lowercase.
    del_field = models.BooleanField(db_column='Del', blank=True, null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.

    def __str__(self):
        return self.status if self.status else ""
    class Meta:
        managed = False
        db_table = 'Tbl_Live_Status'

