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
    path('request-cancellation/<int:request_id>/', views.request_cancellation, name='request_cancellation'),
    path('confirm-cancellation/<int:request_id>/', views.confirm_cancellation, name='confirm_cancellation'),
    path('withdraw-cancellation/<int:request_id>/', views.withdraw_cancellation, name='withdraw_cancellation'),
    path('meeting/<int:request_id>/', views.join_meeting, name='join_meeting'),
]
