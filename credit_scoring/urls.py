from django.urls import path
from .views import dashboard_view, generate_report_view

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('generate-report/', generate_report_view, name='generate-report'),
]
