from django.urls import path,include
from . import views

app_name = 'current_affairs'

urlpatterns = [
    path('create_new/', include("sound_recorders.current_affairs.create_new.urls"), name='current_affairs'),
    path('sound_shift_search/', include("sound_recorders.current_affairs.sound_shift_search.urls"), name='sound_shift_search')
    ]