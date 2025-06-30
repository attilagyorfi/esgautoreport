# esg_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Névtér explicit megadása az include-ban minden apphoz
    path('', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('esgdata/', include(('esgdata.urls', 'esgdata'), namespace='esgdata')),
    path('co2calc/', include(('co2calc.urls', 'co2calc'), namespace='co2calc')),
    path('reports/', include(('reports.urls', 'reports'), namespace='reports')),
    # Ha a 'notifications' appnak van/lesz urls.py-a, azt is ide kell majd venni hasonlóan.
]

# Ez a sor a fejlesztés során a médiafájlok (pl. feltöltött képek) kiszolgálásához kell.
# Győződj meg róla, hogy ez is a fájl végén van.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)