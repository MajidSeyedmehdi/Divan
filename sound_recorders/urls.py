from django.urls import path, include
from . import views

app_name = 'sound_recorders'

urlpatterns = [
    path('', views.recordpage, name='recordpage'),
    path('current_affairs/', include("sound_recorders.current_affairs.urls")),
    path('report/', include("sound_recorders.report.urls")),
    path('shift_audit/', include("sound_recorders.shift_audit.urls")),
    # path('sound_recorders_manager/', include("sound_recorders.sound_recorders_manager.urls"))
    path('soundrecorders_manager/',  include('sound_recorders.soundrecorders_managers.urls')    ),
    path('live_program_audit/', include('sound_recorders.live_program_audit.urls')),
    path('main_program_audit/', include('sound_recorders.live_program_audit.main_live_programs.urls'))


]
