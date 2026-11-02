from django.urls import path, include
from . import views

app_name = 'main_program_audit'

urlpatterns = [
path('', views.import_program_spec_view, name='import_excel'),
]