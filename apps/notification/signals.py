from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from apps.order.models import Order
from .models import Notification

@receiver(post_save, sender=Order)
def update_order_notification(sender, instance, created, **kwargs):
    """
    Signal to create notifications when an order is updated
    This only handles status updates, not order creation
    Order creation notifications are handled in apps.order.signals
    """
    if not created and instance.tracker.has_changed('status'):
        # Notify the customer about the status change
        Notification.objects.create(
            recipient=instance.customer,
            notification_type=Notification.NotificationType.ORDER_UPDATED,
            title=f"Order #{instance.order_number} Updated",
            message=f"Your order #{instance.order_number} status has been updated to {instance.get_status_display()}.",
            related_object_id=instance.id,
            related_object_type='Order'
        )

        # Clear customer's notification cache
        cache_key = f'user_notifications_{instance.customer.id}'
        cache.delete(cache_key)
