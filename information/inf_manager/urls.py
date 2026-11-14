from django.urls import path,include
from . import views


app_name = 'inf_manager'

urlpatterns = [
    path('', views.inf_manager_view, name='inf_manager'),
    path('shift/', include('information.inf_manager.shift.urls', namespace='shift')),
    path('live/', include('information.inf_manager.live.urls', namespace='live')),
    ]