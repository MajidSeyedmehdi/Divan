from django.urls import path
from . import views

app_name = 'person_shift'

urlpatterns = [
    path(
        'person-shifts/<int:id_sound_recorder>/',
        views.person_shift_details,
        name='detail'
    ),
]