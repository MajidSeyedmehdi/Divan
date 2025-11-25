from django.db import models


class ChangePassword(models.Model):
    id = models.IntegerField(db_column="id", primary_key=True)
    first_name = models.CharField(db_column="first_name", max_length=50)
    last_name = models.CharField(db_column="last_name", max_length=50)
    user_name = models.CharField(db_column="username", max_length=10)
    password = models.CharField(db_column="password", max_length=50)

    class Meta:
        db_table = 'auth_user'
        managed = False

