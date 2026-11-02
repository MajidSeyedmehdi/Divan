from django.db import models


class SearchHeader(models.Model):
    GENDER_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن'),
    ]
    MARITAL_CHOICES = [
        ('S', 'مجرد'),
        ('M', 'متاهل'),
        ('D', 'طلاق'),
        ('W', 'فوت همسر')
    ]
    name = models.CharField(max_length=100, db_column='First_name')
    family = models.CharField(max_length=100, db_column='Last_name')
    national_code = models.CharField(max_length=10, db_column='National_code')
    gender = models.CharField(max_length=10, db_column='Gender_status', choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=10, db_column='Marital_status', choices=MARITAL_CHOICES)

    class Meta:
        managed = False
        db_table = 'Tbl_Personally'

class SearchFinancial(models.Model):
    salary_base = models.CharField(max_length=100, db_column='salary_base')
    total_financial = models.CharField(max_length=100, db_column='total_financial')
    baravord = models.CharField(max_length=100, db_column='baravord')

    class Meta:
        managed = False
        db_table = 'Tbl_Financial'

class Insurance(models.Model):
    id_insurance_type = models.CharField(max_length=100, db_column='Id_insurance_type')
    insurance_type = models.CharField(max_length=100, db_column='Insurance_type')

    class Meta:
        managed = False
        db_table = 'Tbl_Insurance_Type'

class Bank(models.Model):
    id_bank = models.CharField(max_length=100, db_column='Id_bank')
    bank = models.CharField(max_length=100, db_column='Bank')

    class Meta:
        managed = False
        db_table = 'Tbl_Bank'

class Accounting(models.Model):
    id_accounting = models.CharField(max_length=100, db_column='Id_account')
    account_number = models.CharField(max_length=100, db_column='Account_number')
    sheba_number = models.CharField(max_length=100, db_column='Sheba_number')

    class Meta:
        managed = False
        db_table = 'Tbl_Bank'

class SearchOfficial(models.Model):
    employment_id = models.CharField(max_length=100, db_column='Employment_id')

    class Meta:
        managed = False
        db_table = 'Tbl_Official'

class ActivityType(models.Model):
    id_activity_type = models.CharField(max_length=100, db_column='Id_activity_type')
    activity_type = models.CharField(max_length=100, db_column='Activity_type')

    class Meta:
        managed = False
        db_table = 'Tbl_Activity_type'

class PaymentType(models.Model):
    id_payment_type = models.CharField(max_length=100, db_column='Id_payment_type')
    payment_type = models.CharField(max_length=100, db_column='Payment_type')

    class Meta:
        managed = False
        db_table = 'Tbl_Activity_type'

class Joblevel(models.Model):
    id_job_level = models.CharField(max_length=100, db_column='Id_levels')
    job_level = models.CharField(max_length=100, db_column='Levels')

    class Meta:
        managed = False
        db_table = 'Tbl_Levels'

class CurrentJob(models.Model):
    id_current_job = models.CharField(max_length=100, db_column='Id_current_job')
    current_job = models.CharField(max_length=100, db_column='Current_job')

    class Meta:
        managed = False
        db_table = 'Tbl_Current_Job'

class HireStatus(models.Model):
    id_hire_status = models.CharField(max_length=100, db_column='Id_hire_status')
    hire_status = models.CharField(max_length=100, db_column='Hire_status')

    class Meta:
        managed = False
        db_table = 'Tbl_Hire_Status'

class JobRelation(models.Model):
    id_job_relation = models.CharField(max_length=100, db_column='Id_job_relation')
    job_relation = models.CharField(max_length=100, db_column='Job_relation')

    class Meta:
        managed = False
        db_table = 'Tbl_Job_Relation'

class JobTitle(models.Model):
    id_job_title = models.CharField(max_length=100, db_column='Id_job_title')
    job_title = models.CharField(max_length=100, db_column='Job_title')

    class Meta:
        managed = False
        db_table = 'Tbl_Job_Title'

class JobUnit(models.Model):
    id_job_unit = models.CharField(max_length=100, db_column='Id_job_unit')
    job_unit = models.CharField(max_length=100, db_column='Job_unit')

    class Meta:
        managed = False
        db_table = 'Tbl_Job_Unit'

