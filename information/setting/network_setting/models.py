from django.db import models
from sound_recorders.current_affairs.sound_shift_search.models import SelectNetwork

class Network_Setting(models.Model):
    id_network_settings = models.IntegerField(primary_key=True, db_column='Id_network_settings')
    id_network = models.ForeignKey(SelectNetwork, on_delete=models.DO_NOTHING, db_column='Id_network')
    shift_count = models.IntegerField(db_column='Shift_count')
    coefficient = models.FloatField(db_column='Coefficient')
    has_live = models.BooleanField(db_column='Has_live')
    payable = models.BooleanField(db_column='Payable')
    active = models.BooleanField(db_column='Active')

    class Meta:
        managed = False
        db_table = 'Tbl_Network_Settings'

