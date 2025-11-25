# change_password/urls.py
from django.urls import path
from .views import changepassword

app_name = 'change_password'

urlpatterns = [
    path('', changepassword, name='change_password'),
]
