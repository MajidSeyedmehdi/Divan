from django.urls import path
from . import views

app_name = 'employment_info'

urlpatterns = [
    path('', views.employment_info_view, name='employment_info'),
]
