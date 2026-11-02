from django.urls import path
from information.setting.network_setting import views

app_name = 'network_setting'

urlpatterns = [
    path('', views.network_setting, name='network_setting'),
] 