from django.urls import path
from . import views

app_name = 'live'

urlpatterns = [
    path( '', views.inf_managers_live, name='live'),
    path('live_details/', views.live_details, name='live_details'),
    path('history/', views.workflow_history, name='workflow_history'),
]