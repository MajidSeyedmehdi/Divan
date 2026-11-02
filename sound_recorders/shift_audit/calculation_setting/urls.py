from django.urls import path,include
from . import views

app_name = 'calculation_setting'

urlpatterns = [
    path('', views.calculation_setting, name='calculation_setting'),
    path('person_shift',include("sound_recorders.shift_audit.calculation_setting.person_shift_details.urls"))
    # path('sound_shift_search/', include("sound_recorders.current_affairs.sound_shift_search.urls"), name='sound_shift_search')
    ]