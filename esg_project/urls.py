# esg_project/urls.py
from django.contrib import admin
from django.urls import path, include # Győződj meg róla, hogy az 'include' itt van
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')), 
    path('data-collection/', include('esgdata.urls')),
    path('accounts/', include('accounts.urls')), 
    path('co2calculator/', include('co2calc.urls')), # <<< EZ A SOR FONTOS! Győződj meg róla, hogy itt van!
]

# Médiafájlok kiszolgálása DEBUG módban (ez már itt volt)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)