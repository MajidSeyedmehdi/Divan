from django.urls import path, include
from . import views

app_name = 'live_program_audit'

urlpatterns = [
path('', views.live_program_audit, name='live_program_audit'),
path('main_live_programs/', include('sound_recorders.live_program_audit.main_live_programs.urls')),

path('live_calculation/', include("sound_recorders.live_program_audit.live_financial_calculation.urls")),

path('manual_live_programs/', include("sound_recorders.live_program_audit.manual_live_programs.urls")),

]