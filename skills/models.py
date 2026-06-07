from django.db import models
from django.conf import settings

class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('Design', 'Design'),
        ('Development', 'Development'),
        ('Writing', 'Writing'),
        ('Music', 'Music'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skills')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Development')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} by {self.user.username}"
