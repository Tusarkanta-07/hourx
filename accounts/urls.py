from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='home'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
