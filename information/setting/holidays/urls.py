from django.urls import path
from information.setting.holidays import views

app_name = 'holidays'

urlpatterns = [
    path('', views.holiday_view, name='holidays'),
] 