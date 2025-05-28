# esgdata/urls.py
from django.urls import path
from . import views # Importáljuk a nézeteket az aktuális appból (esgdata.views)

app_name = 'esgdata' # Az alkalmazás névterének beállítása

urlpatterns = [
    path('new-entry/', views.create_company_data_entry, name='create_company_data_entry'),
    # Ide jöhetnek majd további, az esgdata apphoz kapcsolódó URL-ek a jövőben
    # Pl. egy lista nézet a meglévő adatbevitelekről, szerkesztő nézet, stb.
]