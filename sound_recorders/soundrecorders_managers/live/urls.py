from django.urls import path
from . import views

app_name = "live"

urlpatterns = [
    path("", views.manager_live_summary, name="summary"),
    path("details/<int:id_manual_program>/", views.manager_live_details, name="details"),
]
