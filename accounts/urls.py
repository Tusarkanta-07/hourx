from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='home'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('terms/', views.terms_page, name='terms'),
    path('privacy/', views.privacy_page, name='privacy'),
    path('support/', views.support_page, name='support'),
    path('guidelines/', views.guidelines_page, name='guidelines'),
]
