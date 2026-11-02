from django.urls import path, include
from . import views

app_name = 'sound_recorders'

urlpatterns = [
    path('', views.recordpage, name='recordpage'),
    path('current_affairs/', include("sound_recorders.current_affairs.urls"), name='sound_recorders'),
    path('report/', include("sound_recorders.report.urls"), name='report'),

]
