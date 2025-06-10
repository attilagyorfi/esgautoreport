# accounts/urls.py
from django.urls import path, include
from . import views

app_name = 'accounts' # Ez definiálja az 'accounts' névteret

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    # ÚJ URL a token és link megjelenítéséhez:
    path('registration-step-two/', views.registration_show_token_link_view, name='registration_show_token_link'),

    # Az URL a token-alapú profil kitöltéshez
    path('complete-profile/<uuid:token_uuid>/', views.register_with_token_view, name='register_with_token'),

    path('', include('django.contrib.auth.urls')),
]