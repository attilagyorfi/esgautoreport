# esg_project/urls.py
from django.contrib import admin
from django.urls import path, include 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')), 
    path('data-collection/', include('esgdata.urls')),
    path('accounts/', include('accounts.urls')), 
    path('co2calculator/', include('co2calc.urls')), # <<< ÚJ VAGY ELLENŐRIZENDŐ SOR
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from . import views  # Fontos, hogy a views importálva legyen

app_name = 'co2calc'

urlpatterns = [
    path('ajax/get-emission-factor/', views.get_emission_factor_ajax, name='ajax_get_emission_factor'),
    path('manage-entries/', views.manage_co2_entries_view, name='manage_co2_entries'),  # Itt hivatkozol rá
]