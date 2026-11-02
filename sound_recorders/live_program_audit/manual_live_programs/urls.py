from django.urls import path
from . import views

app_name = 'manual_live_programs'

urlpatterns = [
    path('', views.manual_save, name='manual'),
    path('edit_manual/', views.edit, name='edit_manual'),
]