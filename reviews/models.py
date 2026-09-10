from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from barter.models import BarterRequest

class Review(models.Model):
    barter_request = models.OneToOneField(
        BarterRequest,
        on_delete=models.CASCADE,
        related_name='review',
        null=True,
        blank=True
    )
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    reviewee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        req_info = f" (Request #{self.barter_request_id})" if self.barter_request_id else ""
        return f"{self.rating} stars for {self.reviewee} by {self.reviewer}{req_info}"
