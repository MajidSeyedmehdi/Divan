from django.urls import path
from . import views

app_name = 'shift'

urlpatterns = [
    path( '', views.soundrecorders_managers_shift, name='shift'),

    path('get_final_coating/',views.get_final_coating,name='get_final_coating'),

    path('get_network_coating/',views.get_network_coating,name='get_network_coating'),

    path('get_network_detail/',views.get_network_detail,name='get_network_detail'),

    path('get_workflow_history/',views.get_workflow_history,name='get_workflow_history'),

    path('calculation_setting/',views.calculation_setting,name='calculation_setting'),

    path('person_shift_details/',views.person_shift_details,name='person_shift_details'),
]