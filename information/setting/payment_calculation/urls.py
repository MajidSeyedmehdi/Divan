from django.urls import path
from . import views
app_name = 'payment_calculation'
urlpatterns = [
    path('', views.salary_start_view, name='payment_calculation'),
    path('salary_results', views.salary_result_view, name='salary_results'),
    path('export_excel', views.export_to_excel, name='export_excel'),

]
