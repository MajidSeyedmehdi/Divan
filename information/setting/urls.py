from django.urls import path, include
from . import views

app_name = 'setting'

urlpatterns = [
    path('', views.setting_view, name='setting'),
    path('network_setting/', include(('information.setting.network_setting.urls', 'network_setting'),namespace='network_setting')),
    path('payment_calculation/', include(('information.setting.payment_calculation.urls', 'payment_calculation'),namespace='payment_calculation')),
    path('shift_rate/',include(('information.setting.shift_rate.urls', 'shift_rate'),namespace='shift_rate')),
    path('holidays/',include(('information.setting.holidays.urls', 'holidays'),namespace='holidays')),
    path('financial-period/', include('information.setting.financial_period.urls', namespace='financial_period')),
]

