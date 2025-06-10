# esgdata/urls.py
from django.urls import path
from . import views # Importáljuk a nézeteket az aktuális appból (esgdata.views)

app_name = 'esgdata' # Az alkalmazás névterének beállítása

urlpatterns = [
    # path('new-entry/', views.create_company_data_entry, name='create_company_data_entry'),  # Régi URL kikommentelve

    # Új URL az ESG Jelentés Készítése oldalhoz
    path('create-report/', views.create_esg_report_selection_view, name='create_esg_report_selection'),  # Átnevezzük a régit
    path('fill-questionnaire/<int:company_id>/<int:year>/<str:topic_key>/', views.fill_questionnaire_view, name='fill_questionnaire'),  # ÚJ URL
    path('report-submission-success/', views.report_submission_success_view, name='report_submission_success'), # <<< ÚJ URL
]