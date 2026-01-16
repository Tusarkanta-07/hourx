from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model for HourX.
    Includes time balance and profile information.
    """
    time_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bio = models.TextField(blank=True, help_text="Short bio about yourself and your skills.")
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Password Reset OTP fields
    reset_otp = models.CharField(max_length=6, blank=True, null=True)
    reset_otp_expiry = models.DateTimeField(blank=True, null=True)

    # Skills offered could be a reverse relation to Skills model later.

    def __str__(self):
        return self.username
