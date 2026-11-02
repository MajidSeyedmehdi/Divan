from django.urls import path
from . import views

app_name = 'sound_shift_search'

urlpatterns = [
    path('shift/search/', views.Search_shift, name='sound_shift_search'),

    ]