from django.urls import path
from . import views

app_name = 'inf_manager'

urlpatterns = [
    path('', views.inf_manager_view, name='inf_manager'),
] 