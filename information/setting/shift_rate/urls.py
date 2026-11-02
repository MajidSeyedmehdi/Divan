from django.urls import path
from . import views
app_name = 'shift_rate'
urlpatterns = [
    path('', views.shift_rate_view, name='shift_rate_view'),
    path('get-levels/', views.get_levels, name='get_levels'),
    path('get-shift-numbers/', views.get_shift_names, name='get_shift_names'),
    path('update/', views.update_rate, name='update_rate'),
    path('delete/', views.delete_rate, name='delete_rate'),
    path('add/', views.add_rate, name='add_rate'),
    # path('update/', views.update_shift_rate, name='update'),
    # path('get-levels/', views.get_levels, name='get_levels'),
    # path('get-shift-numbers/', views.get_shift_numbers, name='get_shift_numbers'),
    # path('delete/', views.delete_shift_rate, name='delete'),
    # path('update_shift_rate', views.update_shift_rate(), name='update_shift_rate'),
    # path('export_excel', views.export_to_excel, name='export_excel'),

]
