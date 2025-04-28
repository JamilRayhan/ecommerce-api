from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Notification(models.Model):
    """
    Model for storing notifications for users
    """
    class NotificationType(models.TextChoices):
        ORDER_PLACED = 'ORDER_PLACED', _('Order Placed')
        ORDER_UPDATED = 'ORDER_UPDATED', _('Order Updated')
        PRODUCT_UPDATED = 'PRODUCT_UPDATED', _('Product Updated')
        SYSTEM = 'SYSTEM', _('System Notification')

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f"{self.notification_type}: {self.title} (to: {self.recipient.username})"
