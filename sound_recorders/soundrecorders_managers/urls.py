from django.urls import path,include
from . import views

app_name = 'soundrecorders_manager'

urlpatterns = [
    path('', views.soundrecorders_managers, name='soundrecorders_manager'),
    path('shift/', include('sound_recorders.soundrecorders_managers.shift.urls')),
    path('live/', include('sound_recorders.soundrecorders_managers.live.urls')),

]