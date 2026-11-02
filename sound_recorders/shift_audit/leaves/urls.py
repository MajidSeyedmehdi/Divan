from django.urls import path
from . import views

app_name = 'leaves'

urlpatterns = [
    path('', views.leaves, name='leaves'),
    # path('save_shift_assignments_bulk/', views.save_shift_assignments_bulk, name='save_shift_assignments_bulk'),


    ]