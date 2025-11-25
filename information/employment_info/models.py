from django.db import models
from django.utils import timezone


class Personally(models.Model):
    GENDER_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن'),
    ]

    MARITAL_CHOICES = [
        ('S', 'مجرد'),
        ('M', 'متاهل'),
        ('D', 'طلاق'),
        ('W', 'بیوه')
    ]

    id_personal = models.AutoField(db_column='Id_personal', primary_key=True)  # Field name made lowercase.
    first_name = models.CharField(db_column='First_name', max_length=50,
                                  db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    last_name = models.CharField(db_column='Last_name', max_length=50,
                                 db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    father_name = models.CharField(db_column='Father_name', max_length=50,
                                   db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    birth_number = models.CharField(db_column='Birth_number', max_length=10,
                                    db_collation='Persian_100_CI_AS')
    gender_status = models.CharField(
        db_column='Gender_status',
        max_length=10,
        choices=GENDER_CHOICES,
        db_collation='Persian_100_CI_AI'
    )  # Field name made lowercase.
    marital_status = models.CharField(
        db_column='Marital_status',
        max_length=10,
        choices=MARITAL_CHOICES,
        db_collation='Persian_100_CI_AI'
    )  # Field name made lowercase.
    national_code = models.CharField(db_column='National_code', max_length=50,
                                     db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    birth_date = models.CharField(db_column='Birth_date', max_length=50,
                                  db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    birth_city = models.CharField(db_column='Birth_city', max_length=20,
                                  db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=50, db_collation='Persian_100_CI_AS',
                             blank=True)  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    user_name = models.CharField(db_column='User_name', max_length=50,
                                 db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Personally'


class Location(models.Model):
    id_location = models.AutoField(db_column='Id_location', primary_key=True)  # Field name made lowercase.
    id_personal = models.ForeignKey('Personally', on_delete=models.PROTECT,
                                    db_column='Id_personal', related_name='+')  # Field name made lowercase.
    postal_code = models.CharField(db_column='Postal_code', max_length=20,
                                   db_collation='Persian_100_CI_AS',
                                   null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=50,
                            db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    address = models.CharField(db_column='Address', max_length=200,
                               db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    user_name = models.CharField(db_column='User_name', max_length=50, db_collation='Persian_100_CI_AS')
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Location'


class Family(models.Model):
    TYPE = [
        ('S', 'همسر'),
        ('CHM', 'فرزند پسر'),
        ('CHF', 'فرزند دختر'),
    ]
    id_family = models.AutoField(db_column='Id_family', primary_key=True)  # Field name made lowercase.
    id_personal = models.ForeignKey('Personally', models.DO_NOTHING,
                                    db_column='Id_personal')  # Field name made lowercase.
    first_name = models.CharField(db_column='First_name', max_length=50,
                                  db_collation='Persian_100_CI_AS', blank=True,
                                  null=True)  # Field name made lowercase.
    last_name = models.CharField(db_column='Last_name', max_length=50,
                                 db_collation='Persian_100_CI_AS', blank=True,
                                 null=True)  # Field name made lowercase.
    birth_date = models.CharField(db_column='Birth_date', max_length=50,
                                  db_collation='Persian_100_CI_AS', blank=True,
                                  null=True)  # Field name made lowercase.
    national_code = models.CharField(db_column='National_code', max_length=12,
                                     db_collation='Persian_100_CI_AS', blank=True,
                                     null=True)  # Field name made lowercase.
    type = models.CharField(
        db_column='Type',
        max_length=50,
        choices=TYPE,
        db_collation='Persian_100_CI_AS', default=None,
    )
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    user_name = models.CharField(db_column='User_name', max_length=50, db_collation='Persian_100_CI_AS')
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Family'


class Education(models.Model):
    id_education = models.AutoField(db_column='Id_education', primary_key=True)  # Field name made lowercase.
    id_personal = models.ForeignKey('Personally', on_delete=models.PROTECT,
                                    db_column='Id_personal', related_name='+')  # Field name made lowercase.
    id_educational_level = models.ForeignKey('Educational_level', on_delete=models.PROTECT,
                                             db_column='Id_educational_level', related_name='+')
    field_study = models.CharField(db_column='Field_study', max_length=50,
                                   db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    university = models.CharField(db_column='University', max_length=50,
                                  db_collation='Persian_100_CI_AS', default=None)
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    user_name = models.CharField(db_column='User_name', max_length=50, db_collation='Persian_100_CI_AS')
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Education'


class Educational_level(models.Model):
    id_educational_level = models.AutoField(db_column='Id_educational_level',
                                            primary_key=True)  # Field name made lowercase
    educational_level = models.CharField(db_column='Educational_level', max_length=50,
                                         db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Educational_level'


class Phone(models.Model):
    id_phone = models.AutoField(db_column='Id_phone', primary_key=True)
    id_personal = models.ForeignKey('Personally', on_delete=models.PROTECT, db_column='Id_personal', related_name='+')
    phone_number = models.CharField(db_column='Phone_number', max_length=15,
                                    db_collation='Persian_100_CI_AS')
    mobile_number = models.CharField(db_column='Mobile_number', max_length=15,
                                     db_collation='Persian_100_CI_AS')
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    user_name = models.CharField(db_column='User_name', max_length=50, db_collation='Persian_100_CI_AS')
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Phone'

class Insurance_Type(models.Model):
    id_insurance_type = models.AutoField(db_column='Id_insurance_type', primary_key=True)  # Field name made lowercase.
    insurance_type = models.CharField(db_column='Insurance_type', max_length=50,
                                   db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Insurance_Type'

class Financial(models.Model):
    id_financial = models.AutoField(db_column='Id_financial', primary_key=True)  # Field name made lowercase.
    id_personal = models.ForeignKey('Personally', models.DO_NOTHING, db_column='Id_personal')
    salary_base = models.BigIntegerField(db_column='salary_base',default=0)  # Field name made lowercase.
    id_insurance_type = models.ForeignKey('Insurance_Type', models.DO_NOTHING, db_column='Id_insurance_type')
    insurance_number = models.CharField(db_column='Insurance_number', max_length=50,
                                        db_collation='Persian_100_CI_AS',blank=True,null=True)  # Field name made lowercase.
    housing_right = models.BigIntegerField(db_column='Housing_right',default=0,blank=True,null=True)  # Field name made lowercase.
    children_right = models.BigIntegerField(db_column='Children_right', default=0,blank=True,null=True)
    wife_right = models.BigIntegerField(db_column='Wife_right', default=0, blank=True, null=True)
    kharobar = models.BigIntegerField(db_column='Kharobar', default=0,blank=True,null=True)  # Field name made lowercase.
    sanavat = models.BigIntegerField(db_column='Sanavat', default=0,blank=True,null=True)
    eydi = models.BigIntegerField(db_column='Eydi', default=0,blank=True,null=True)
    f_shoghl = models.BigIntegerField(db_column='F_shoghl', default=0,blank=True,null=True)
    f_amoozesh = models.BigIntegerField(db_column='F_amoozesh', default=0, blank=True, null=True)
    f_mohandesi = models.BigIntegerField(db_column='F_mohandesi', default=0,blank=True,null=True)
    f_abohava = models.BigIntegerField(db_column='F_abohava', default=0,blank=True,null=True)
    f_mahroomiat = models.BigIntegerField(db_column='F_mahroomiat', default=0,blank=True,null=True)
    f_isargari = models.BigIntegerField(db_column='F_Isargari', default=0,blank=True,null=True)
    f_51 = models.BigIntegerField(db_column='F_51', default=0,blank=True,null=True)
    f_sakhti_kar = models.BigIntegerField(db_column='F_sakhti_kar', default=0,blank=True,null=True)
    # f_marzi = models.BigIntegerField(db_column='F_marzi', default=0,blank=True,null=True)
    # f_enteghal = models.BigIntegerField(db_column='F_enteghal', default=0,blank=True,null=True)
    # f_jazb_mahroom = models.BigIntegerField(db_column='F_jazb_mahroom', default=0,blank=True,null=True)
    management_right = models.BigIntegerField(db_column='Management_right', default=0,blank=True,null=True)
    f_resaneh = models.BigIntegerField(db_column='F_resaneh', default=0,blank=True,null=True)
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    user_name = models.CharField(db_column='User_name', max_length=50,
                                 db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Financial'


class Bank(models.Model):
    id_bank = models.AutoField(db_column='Id_bank', primary_key=True)
    bank = models.CharField(db_column='Bank', max_length=50, db_collation='Persian_100_CI_AS')
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Bank'


class Accounting(models.Model):
    id_account = models.AutoField(db_column='Id_account', primary_key=True)
    id_financial = models.ForeignKey('Financial', on_delete=models.PROTECT, db_column='Id_financial', related_name='+')
    id_bank = models.ForeignKey('Bank', on_delete=models.PROTECT, db_column='Id_bank', related_name='+')
    account_number = models.CharField(db_column='Account_number', max_length=50,
                                      db_collation='Persian_100_CI_AS')
    sheba_number = models.CharField(db_column='Sheba_number', max_length=50,
                                    db_collation='Persian_100_CI_AS')
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    user_name = models.CharField(db_column='User_name', max_length=50, db_collation='Persian_100_CI_AS')
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Accounting'


class CurrentJob(models.Model):
    id_current_job = models.AutoField(db_column='Id_current_job', primary_key=True)  # Field name made lowercase.
    current_job = models.CharField(db_column='Current_job', max_length=50,
                                   db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Current_Job'


class HireStatus(models.Model):
    id_hire_status = models.AutoField(db_column='Id_hire_status', primary_key=True)  # Field name made lowercase.
    hire_status = models.CharField(db_column='Hire_status', max_length=50,
                                   db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Hire_Status'


class JobTitle(models.Model):
    id_job_title = models.AutoField(db_column='Id_job_title', primary_key=True)  # Field name made lowercase.
    job_title = models.CharField(db_column='Job_title', max_length=50,
                                 db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Job_Title'


class JobUnit(models.Model):
    id_job_unit = models.AutoField(db_column='Id_job_unit', primary_key=True)  # Field name made lowercase.
    job_unit = models.CharField(db_column='Job_unit', max_length=50,
                                db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Job_Unit'


class Mandatory_Hours(models.Model):
    id_mandatory_hours = models.AutoField(db_column='Id_Mandatory_hours',
                                          primary_key=True)  # Field name made lowercase.
    mandatory_hours = models.CharField(db_column='Mandatory_hours', max_length=20,
                                       db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Mandatory_Hours'

class Payment_Type(models.Model):
    id_payment_type = models.AutoField(db_column='Id_payment_type',
                                          primary_key=True)  # Field name made lowercase.
    payment_type = models.CharField(db_column='Payment_type', max_length=50,
                                       db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Payment_Type'

class Activity_Type(models.Model):
    id_activity_type = models.AutoField(db_column='Id_activity_type',
                                          primary_key=True)  # Field name made lowercase.
    activity_type = models.CharField(db_column='Activity_type', max_length=50,
                                       db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Activity_Type'

class Levels(models.Model):
    id_levels = models.AutoField(db_column='Id_levels',
                                          primary_key=True )  # Field name made lowercase.
    levels = models.CharField(db_column='Levels', max_length=20,
                                       db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Levels'

class Official(models.Model):

    id_official = models.AutoField(db_column='Id_official', primary_key=True)  # Field name made lowercase.
    id_personal = models.ForeignKey('Personally', models.DO_NOTHING,
                                    db_column='Id_personal')  # Field name made lowercase.
    id_mandatory_hours = models.ForeignKey('Mandatory_Hours', models.DO_NOTHING,
                                           db_column='Id_mandatory_hours')  # Field name made lowercase.
    employment_id = models.CharField(db_column='Employment_id', max_length=10,
                                     db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    id_activity_type = models.ForeignKey('Activity_Type', models.DO_NOTHING,db_column='Id_activity_type')
    id_payment_type = models.ForeignKey('Payment_Type', models.DO_NOTHING,db_column='Id_payment_type')
    isargari = models.BooleanField(db_column='Isargari', default=False, null=False)
    basij = models.BooleanField(db_column='Basij', default=False, null=False)
    id_job_unit = models.ForeignKey('JobUnit', models.DO_NOTHING, db_column='Id_job_unit')  # Field name made lowercase.
    id_job_title = models.ForeignKey('JobTitle', models.DO_NOTHING,
                                     db_column='Id_Job_title')  # Field name made lowercase.
    id_job_level = models.ForeignKey ('Levels', models.DO_NOTHING, db_column='Id_job_level',related_name='officials_job_level') # Field name made lowercase.
    id_current_job = models.ForeignKey('CurrentJob', models.DO_NOTHING,
                                       db_column='Id_current_job')  # Field name made lowercase.
    id_current_job_level = models.ForeignKey ('Levels', models.DO_NOTHING, db_column='Id_current_job_level',related_name='officials_current_job_level')
    id_hire_status = models.ForeignKey('HireStatus', models.DO_NOTHING,
                                       db_column='Id_hire_status')  # Field name made lowercase.

    id_job_relation = models.ForeignKey('JobRelation', models.DO_NOTHING,
                                        db_column='Id_job_relation')
    hire_date = models.CharField(db_column='Hire_date', max_length=50,
                                 db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    last_promotion_date = models.CharField(db_column='Last_promotion_date', max_length=50,
                                           db_collation='Persian_100_CI_AS', blank=True,
                                           null=True)
    programming_code = models.CharField(db_column='Programming_code', max_length=50,
                                        db_collation='Persian_100_CI_AS', blank=True,
                                        null=True)
    retirement_date = models.CharField(db_column='Retirement_date', max_length=50,
                                       db_collation='Persian_100_CI_AS', blank=True,
                                       null=True)
    end_date_cooperation = models.CharField(db_column='End_date_cooperation', max_length=50,
                                            db_collation='Persian_100_CI_AS', blank=True,
                                            null=True)

    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    user_name = models.CharField(db_column='User_name', max_length=50, db_collation='Persian_100_CI_AS')
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Official'


class OfficialHire(models.Model):
    id_official_hire = models.AutoField(db_column='Id_official_hire', primary_key=True)  # Field name made lowercase.
    id_official = models.ForeignKey('Official', on_delete=models.PROTECT, db_column='Id_official', related_name='+')
    id_hire_status = models.ForeignKey('HireStatus', on_delete=models.PROTECT, db_column='Id_hire_status',
                                       related_name='+')
    active = models.BooleanField(db_column='Active', default=True, null=False)
    user_name = models.CharField(db_column='User_name', max_length=50, db_collation='Persian_100_CI_AS')
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Official_Hire'


class OfficialActivity(models.Model):
    id_official_activity = models.AutoField(db_column='Id_official_activity',
                                            primary_key=True)  # Field name made lowercase.
    id_official = models.ForeignKey('Official', on_delete=models.PROTECT, db_column='Id_official', related_name='+')
    id_activity_type = models.ForeignKey('Activity_Type', on_delete=models.PROTECT, db_column='Id_activity_type',
                                      related_name='+', default=None)
    active = models.BooleanField(db_column='Active', default=True, null=False)
    user_name = models.CharField(db_column='User_name', max_length=50, db_collation='Persian_100_CI_AS')
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Official_Activity'


class JobRelation(models.Model):
    id_job_relation = models.AutoField(db_column='Id_job_relation', primary_key=True)  # Field name made lowercase.
    job_relation = models.CharField(db_column='Job_relation', max_length=50,
                                    db_collation='Persian_100_CI_AS')  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Job_Relation'


class OfficialJobRelation(models.Model):
    id_official_job_relation = models.AutoField(db_column='Id_official_job_relation',
                                                primary_key=True)  # Field name made lowercase.
    id_official = models.ForeignKey('Official', on_delete=models.PROTECT, db_column='Id_official', related_name='+')
    id_job_relation = models.ForeignKey('JobRelation', on_delete=models.PROTECT, db_column='Id_job_relation',
                                        related_name='+')
    active = models.BooleanField(db_column='Active', default=True, null=False)
    user_name = models.CharField(db_column='User_name', max_length=50, db_collation='Persian_100_CI_AS')
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Official_Job_Relation'


class OfficialPaymentType(models.Model):
    id_official_payment_type = models.AutoField(db_column='Id_official_payment_type',
                                                primary_key=True)  # Field name made lowercase.
    id_official = models.ForeignKey('Official', on_delete=models.PROTECT, db_column='Id_official', related_name='+')
    id_payment_type = models.ForeignKey('Payment_Type', on_delete=models.PROTECT, db_column='Id_payment_type',
                                     related_name='+', default=None)
    active = models.BooleanField(db_column='Active', default=True, null=False)
    user_name = models.CharField(db_column='User_name', max_length=50, db_collation='Persian_100_CI_AS')
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Official_Payment_Type'


class OfficialJobUnit(models.Model):
    id_official_job_unit = models.AutoField(db_column='Id_official_job_unit', primary_key=True)
    id_official = models.ForeignKey('Official', on_delete=models.PROTECT, db_column='Id_official', related_name='+')
    id_job_unit = models.ForeignKey('JobUnit', on_delete=models.PROTECT, db_column='Id_job_unit', related_name='+')
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    user_name = models.CharField(db_column='User_name', max_length=50, db_collation='Persian_100_CI_AS',
                                 default=None)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Official_Job_Unit'


# class ProgrammingCode(models.Model):
#     id_programming_code = models.AutoField(db_column='Id_programming_code', primary_key=True)
#     is_active = models.BooleanField(db_column='Is_active', default=True, null=False)
#     active = models.BooleanField(db_column='Active', default=True, null=False)
#     del_field = models.BooleanField(db_column='Del', default=False, null=False)
#     update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)
#
#     class Meta:
#         managed = False
#         db_table = 'Tbl_Programming_Code'


class Formula(models.Model):
    id_formula = models.AutoField(db_column='Id_formula', primary_key=True)
    id_hire_status = models.ForeignKey('HireStatus', on_delete=models.PROTECT, db_column='Id_hire_status',
                                       related_name='+')
    active = models.BooleanField(db_column='Active', default=True, null=False)
    del_field = models.BooleanField(db_column='Del', default=False, null=False)
    user_name = models.CharField(db_column='User_name', max_length=50, db_collation='Persian_100_CI_AS',
                                 default=None)
    update_date = models.DateTimeField(db_column='Update_date', default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Tbl_Formula'
