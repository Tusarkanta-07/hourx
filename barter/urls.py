from django.urls import path
from . import views

urlpatterns = [
    path('request/<int:skill_id>/', views.create_request, name='create_request'),
    path('received/', views.received_requests, name='received_requests'),
    path('sent/', views.sent_requests, name='sent_requests'),
    path('accept/<int:request_id>/', views.accept_request, name='accept_request'),
    path('complete/<int:request_id>/', views.complete_request, name='complete_request'),
    path('reject/<int:request_id>/', views.reject_request, name='reject_request'),
    path('cancel/<int:request_id>/', views.cancel_request, name='cancel_request'),
    path('meeting/<int:request_id>/', views.join_meeting, name='join_meeting'),
]
