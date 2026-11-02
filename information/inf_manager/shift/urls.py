from django.urls import path
from . import views

app_name = 'shift'

urlpatterns = [
    path('', views.shift, name='shift'),
    path('get-workflow-history/', views.get_workflow_history, name='get_workflow_history'),
    path('get_shift_details/', views.get_shift_details, name='get_shift_details'),
    path('get_final_coating/', views.get_final_coating, name='get_final_coating'),
    path('get_network_coating/', views.get_network_coating, name='get_network_coating'),
    path('get_network_detail/', views.get_network_detail, name='get_network_detail'),
]