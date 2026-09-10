import uuid
from django.db import models
from django.conf import settings
from skills.models import Skill

class BarterRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
        ('CANCELED', 'Canceled'),
    ]

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_requests')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    hours = models.PositiveIntegerField(default=1)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    is_escrowed = models.BooleanField(default=False)
    meeting_token = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    cancellation_requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='cancellation_requests_initiated'
    )
    cancellation_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_cancellation_pending(self):
        return bool(self.cancellation_requested_by)

    def __str__(self):
        return f"Request from {self.sender} to {self.receiver} for {self.skill}"
