from django.urls import path
from . import views

app_name = 'report'

urlpatterns = [
    # path('api/report/shift', views.report_shift, name='report_shift')
    path("set_params/", views.set_params, name="set_params"),
    path("viewer/", views.report_viewer, name="report_viewer"),
]