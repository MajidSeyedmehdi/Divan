from django.urls import path
from .views import search_input, export_to_excel_view

app_name='search'
urlpatterns = [
    path('', search_input, name = "search"),
    path('export_excel/', export_to_excel_view, name='export_excel'),
]