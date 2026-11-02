from django.urls import path
from . import views

app_name = 'create_new'

urlpatterns = [
    path('', views.create_new, name='new_job'),
    path('save_shift_assignments_bulk/', views.save_shift_assignments_bulk, name='save_shift_assignments_bulk'),
    path('get_networ_shifts/', views.get_network_shifts, name='get_network_shifts'),
    path('swap_network_assignment/', views.swap_network_assignment, name='swap_network_assignment'),
]