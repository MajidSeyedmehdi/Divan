from django.db import models

class Personal(models.Model):
    id_personal = models.IntegerField(db_column="Id_personal", primary_key=True)
    first_name = models.CharField(db_column="First_name", max_length=50)
    last_name = models.CharField(db_column="Last_name", max_length=50)
    national_code = models.CharField(db_column="National_code", max_length=10)


    class Meta:
        db_table = 'Tbl_Personally'
        managed = False
class Financial(models.Model):
    id_financial = models.IntegerField(db_column="Id_financial", primary_key=True)
    salary_base = models.BigIntegerField(db_column="Salary_base")
    id_personal = models.IntegerField(db_column="Id_personal")
    wife_right = models.BigIntegerField(db_column='Wife_right')
    Housing_right = models.BigIntegerField(db_column='Housing_right')
    children_right = models.BigIntegerField(db_column='Children_right')
    kharobar = models.BigIntegerField(db_column='Kharobar')
    sanavat = models.BigIntegerField(db_column='Sanavat')
    eydi = models.BigIntegerField(db_column='Eydi')
    f_shoghl = models.BigIntegerField(db_column='f_shoghl')
    f_amoozesh = models.BigIntegerField(db_column='f_amoozesh')
    f_mohandesi = models.BigIntegerField(db_column='f_mohandesi')
    f_abohava = models.BigIntegerField(db_column='f_abohava')
    f_mahroomiat = models.BigIntegerField(db_column='f_mahroomiat')
    f_isargari = models.BigIntegerField(db_column='f_isargari')
    f_51 = models.BigIntegerField(db_column='f_51')
    f_sakhti_kar = models.BigIntegerField(db_column='f_sakhti_kar')
    # f_marzi = models.BigIntegerField(db_column='f_marzi')
    # f_enteghal = models.BigIntegerField(db_column='f_enteghal')
    # f_jazb_mahroom = models.BigIntegerField(db_column='f_jazb_mahroom')
    management_right = models.BigIntegerField(db_column='Management_right')
    f_resaneh = models.BigIntegerField(db_column='f_resaneh')

    class Meta:
        db_table = 'Tbl_Financial'
        managed = False

class JobRelation(models.Model):
    id_job_relation = models.IntegerField(db_column="Id_job_relation", primary_key=True)
    title_job_rel = models.CharField(db_column="job_relation", max_length=100)

    def to_dict(self):
        return {
            "id_job_relation": self.id_job_relation,
            "title_job_rel": self.title_job_rel
        }

    def __str__(self):
        return self.title_job_rel

    class Meta:
        db_table = 'Tbl_Job_Relation'
        managed = False

class JobTittle(models.Model):
    id_job_tittle = models.IntegerField(db_column="Id_job_title", primary_key=True)
    title_job_ti = models.CharField(db_column="Job_title", max_length=100)

    def __str__(self):
        return self.title_job_ti

    class Meta:
        db_table = 'Tbl_Job_Title'
        managed = False

class JobLevel(models.Model):
    id_job_tittle = models.IntegerField(db_column="Id_levels", primary_key=True)
    title_job_le = models.CharField(db_column="Levels", max_length=100)

    def __str__(self):
        return self.title_job_le

    class Meta:
        db_table = 'Tbl_Levels'
        managed = False

class Hirestatus(models.Model):
    id_hire_status = models.IntegerField(db_column="Id_hire_status", primary_key=True)
    hire_status_title = models.CharField(db_column="Hire_status", max_length=100)

    def __str__(self):
        return self.hire_status_title

    class Meta:
        db_table = 'Tbl_Hire_Status'
        managed = False

class JobUnit(models.Model):
    id_job_unit = models.IntegerField(db_column="Id_job_unit", primary_key=True)
    title_job_un = models.CharField(db_column="Job_unit", max_length=100)

    def __str__(self):
        return self.title_job_un

    class Meta:
        db_table = 'Tbl_Job_Unit'
        managed = False

class Official(models.Model):
    id_official = models.IntegerField(db_column="Id_official", primary_key=True)
    id_personal = models.IntegerField(db_column="Id_personal")
    hire_status = models.CharField(db_column="Id_hire_status", max_length=50)
    job_relation = models.ForeignKey(JobRelation, on_delete=models.DO_NOTHING,db_column="Id_job_relation")
    job_title = models.ForeignKey(JobTittle, on_delete=models.DO_NOTHING,db_column="Id_job_title")
    job_level = models.ForeignKey(JobLevel, on_delete=models.DO_NOTHING, db_column="Id_job_level")
    job_unit = models.ForeignKey(JobUnit, on_delete=models.DO_NOTHING, db_column="Id_job_unit")

    class Meta:
        db_table = 'Tbl_Official'
        managed = False

class FormulaSetting(models.Model):
    id_formula = models.AutoField(db_column="Id_formula", primary_key=True)
    hire_status = models.IntegerField(db_column="Id_hire_status", unique=True)
    formula = models.CharField(db_column="Formula", max_length=255)

    class Meta:
        db_table = 'Tbl_Formula'
        managed = False