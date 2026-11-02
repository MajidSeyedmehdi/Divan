from django.urls import path, include
from . import views

app_name = 'live_financial_calculation'

urlpatterns = [
    path('financial/summary/', views.live_programs_summary_view, name='live_programs_summary'),
    path('financial/details/<int:id_manual_program>/', views.live_program_details_view, name='live_program_details'),
]