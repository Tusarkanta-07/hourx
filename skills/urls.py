from django.urls import path
from . import views

urlpatterns = [
    path('', views.skill_list, name='skill_list'),
    path('add/', views.skill_create, name='skill_create'),
    path('<int:pk>/', views.skill_detail, name='skill_detail'),
    path('<int:pk>/edit/', views.skill_edit, name='skill_edit'),
    path('<int:pk>/delete/', views.skill_delete, name='skill_delete'),
]
