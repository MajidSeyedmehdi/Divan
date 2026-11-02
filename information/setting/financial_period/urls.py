from django.urls import path
from . import views

app_name = 'financial_Period'  # namespace برای استفاده در templates

urlpatterns = [
    path('', views.create_financial_period, name='create_financial_period'),

]