from django.urls import path
from . import views

app_name = 'create_new'

urlpatterns = [
    path('', views.create_new, name='new_job'),
    path('save_shift_assignments_bulk/', views.save_shift_assignments_bulk, name='save_shift_assignments_bulk'),


    ]