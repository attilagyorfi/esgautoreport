# esgdata/urls.py
from django.urls import path
from . import views

app_name = 'esgdata'

urlpatterns = [
    path('create-report/', views.create_report_selection_view, name='create_report_selection'),
    path('fill-report/<int:report_id>/', views.fill_report_view, name='fill_report'),
]