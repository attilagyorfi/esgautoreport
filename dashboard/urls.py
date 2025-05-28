# dashboard/urls.py
from django.urls import path
from . import views # Importáljuk a nézeteket az aktuális appból

app_name = 'dashboard' # Ajánlott az app nevének megadása névtérként

urlpatterns = [
    path('', views.home_view, name='home'), # Az app gyökere (pl. /dashboard/) erre a nézetre mutat
    path('rolunk/', views.about_us_view, name='about_us'),
    path('kapcsolat/', views.contact_view, name='contact'),
    path('tudastar/', views.knowledge_base_view, name='knowledge_base'),
    path('company-setup/', views.company_setup_view, name='company_setup'),

]