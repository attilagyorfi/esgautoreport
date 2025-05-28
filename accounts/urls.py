# accounts/urls.py
from django.urls import path, include # Győződj meg róla, hogy az 'include' itt van
from . import views

app_name = 'accounts' # Ez definiálja az 'accounts' névteret

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('registration-pending/', views.registration_pending_view, name='registration_pending'),

    # A Django beépített auth URL-jei (login, logout, password_change, password_reset, stb.)
    # Mivel az app_name 'accounts', ezek az URL-ek pl. 'accounts:login', 'accounts:logout' néven is elérhetők,
    # de a 'login', 'logout' globális neveknek is működniük kellene, ha a settings.py-ben
    # a LOGIN_URL és LOGOUT_REDIRECT_URL nincs névtérhez kötve.
    # A biztonság kedvéért, hogy a 'logout' és 'login' globális nevek biztosan működjenek a sablonban,
    # a django.contrib.auth.urls-t a projekt fő urls.py-jában is hagyhatjuk, vagy itt expliciten nem névtérbe tesszük.
    # De a jelenlegi felállás szerint (ahol a projekt urls.py-ja az accounts.urls-t hívja meg az 'accounts/' alatt)
    # a {% url 'logout' %} keresésnek meg kellene találnia.
    path('', include('django.contrib.auth.urls')),
]