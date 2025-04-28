from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderItem
from django.core.mail import send_mail
from django.conf import settings
from apps.notification.models import Notification
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    """
    Signal to handle new order creation
    """
    if created:
        # Log the order creation
        logger.info(f"New order created: {instance.order_number}")

        # Create notification for the customer
        Notification.objects.create(
            recipient=instance.customer,
            notification_type=Notification.NotificationType.ORDER_PLACED,
            title=f"Order #{instance.order_number} Placed",
            message=f"Your order #{instance.order_number} has been placed successfully. Total: ${instance.total_price}",
            related_object_id=instance.id,
            related_object_type='Order'
        )

        # Clear customer's notification cache
        cache_key = f'user_notifications_{instance.customer.id}'
        cache.delete(cache_key)

        # In a real application, you might want to send an email to the customer
        try:
            send_mail(
                f'Order Confirmation #{instance.order_number}',
                f'Thank you for your order. Your order number is {instance.order_number}.',
                settings.DEFAULT_FROM_EMAIL,
                [instance.customer.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send order confirmation email: {str(e)}")

@receiver(post_save, sender=OrderItem)
def notify_vendor(sender, instance, created, **kwargs):
    """
    Signal to notify vendors when their products are ordered
    """
    if created:
        vendor = instance.product.vendor
        vendor_user = vendor.user
        vendor_email = vendor_user.email
        order = instance.order

        # Log the notification
        logger.info(f"Notifying vendor {vendor.company_name} about new order item")

        # Create notification for the vendor
        Notification.objects.create(
            recipient=vendor_user,
            notification_type=Notification.NotificationType.ORDER_PLACED,
            title=f"New Order #{order.order_number}",
            message=f"You have received a new order #{order.order_number} from {order.customer.username} for {instance.product.name}. Quantity: {instance.quantity}.",
            related_object_id=order.id,
            related_object_type='Order'
        )

        # Clear vendor's notification cache
        cache_key = f'user_notifications_{vendor_user.id}'
        cache.delete(cache_key)

        # In a real application, you might want to send an email to the vendor
        try:
            send_mail(
                f'New Order for Your Product',
                f'You have a new order for {instance.product.name}. Quantity: {instance.quantity}.',
                settings.DEFAULT_FROM_EMAIL,
                [vendor_email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send vendor notification email: {str(e)}")
