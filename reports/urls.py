# reports/urls.py
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('generate/<int:request_id>/', views.generate_report_view, name='generate_report'),
]