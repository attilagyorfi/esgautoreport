# esgdata/urls.py
from django.urls import path
from . import views

app_name = 'esgdata'

urlpatterns = [
    # 1. URL: A kiválasztó oldal, amire a menüpontok és gombok mutatnak
    # A nézet neve a views.py-ban: create_report_selection_view
    # Az URL neve: 'create_report_selection'
    path('create-report/', views.create_report_selection_view, name='create_report_selection'),
    
    # 2. URL: A kérdőív kitöltő oldal
    path('fill-report/<int:company_id>/<int:year>/<str:report_type_key>/', views.fill_report_view, name='fill_report'),
    
    # 3. URL: A sikeres mentést visszaigazoló oldal
    path('report-submission-success/', views.report_submission_success_view, name='report_submission_success'),
]