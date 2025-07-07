# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('rolunk/', views.about_us, name='about_us'),
    path('tudastar/', views.knowledge_base, name='knowledge_base'),
    path('kapcsolat/', views.contact, name='contact'),
]