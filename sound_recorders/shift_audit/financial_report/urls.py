from django.urls import path,include
from . import views

app_name = 'financial_report'

urlpatterns = [
    path('', views.financial_report, name='financial_report'),
    path('get_final_coating/', views.get_final_coating, name='get_final_coating'),
    path('get_network_coating/', views.get_network_coating, name='get_network_coating'),
    path('get_network_detail/', views.get_network_detail, name='get_network_detail'),
    path('get_workflow_history/', views.get_workflow_history, name='get_workflow_history'),
    ]