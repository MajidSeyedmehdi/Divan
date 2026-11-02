from django.urls import path,include
from . import views

app_name = 'shift_audit'

urlpatterns = [
    path('leaves/', include("sound_recorders.shift_audit.leaves.urls"), name='leaves'),
    path('calculation_setting/', include("sound_recorders.shift_audit.calculation_setting.urls"), name='leaves'),
    # path('sound_shift_search/', include("sound_recorders.current_affairs.sound_shift_search.urls"), name='sound_shift_search')
    path('financial_report/', include("sound_recorders.shift_audit.financial_report.urls"), name='financial_report'),


    ]