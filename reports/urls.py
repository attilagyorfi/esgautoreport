# reports/urls.py
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # JAVÍTVA: Hozzáadtuk a <int:report_id> paramétert az URL-hez
    path('view/<int:report_id>/', views.generate_html_report, name='view_report'),
    
    # Ezt is javítjuk, hogy a PDF letöltés is tudja, melyik riportot töltse le
    path('download-pdf/<int:report_id>/', views.generate_pdf_report, name='download_pdf_report'),
]