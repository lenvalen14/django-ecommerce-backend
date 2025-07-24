from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class NotificationType(models.TextChoices):
    ORDER = 'order', 'Order'
    SYSTEM = 'system', 'System'
    PROMOTION = 'promotion', 'Promotion'
    OTHER = 'other', 'Other'

class Notification(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.OTHER,
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
