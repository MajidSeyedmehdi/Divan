from django.urls import path, include
from . import views

app_name = 'information'

urlpatterns = [
    path('inf_manager/', include("information.inf_manager.urls")),
    path('employment_info/', include('information.employment_info.urls')),
    path('activity_permit/', include('information.activity_permit.urls')),
    path('search/', include('information.search.urls',namespace='search')),
    path('setting/', include('information.setting.urls')),
    path('', views.information_view, name='information'),

            ]