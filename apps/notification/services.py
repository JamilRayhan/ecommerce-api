from apps.core.services import BaseService
from .repositories import NotificationRepository
from .models import Notification
from typing import Optional, List, Dict, Any, Union
from django.db.models import QuerySet


class NotificationService(BaseService):
    """
    Service for Notification model
    """
    
    def __init__(self):
        super().__init__(NotificationRepository())
    
    def get_by_recipient_id(self, recipient_id: int) -> QuerySet:
        """
        Get notifications by recipient ID
        """
        return self.repository.get_by_recipient_id(recipient_id)
    
    def get_unread_by_recipient_id(self, recipient_id: int) -> QuerySet:
        """
        Get unread notifications by recipient ID
        """
        return self.repository.get_unread_by_recipient_id(recipient_id)
    
    def get_by_type(self, notification_type: str) -> QuerySet:
        """
        Get notifications by type
        """
        return self.repository.get_by_type(notification_type)
    
    def get_by_related_object(self, object_type: str, object_id: int) -> QuerySet:
        """
        Get notifications by related object
        """
        return self.repository.get_by_related_object(object_type, object_id)
    
    def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        """
        Mark a notification as read
        """
        return self.repository.mark_as_read(notification_id)
    
    def mark_all_as_read(self, recipient_id: int) -> int:
        """
        Mark all notifications for a recipient as read
        """
        return self.repository.mark_all_as_read(recipient_id)
    
    def create_notification(self, recipient_id: int, notification_type: str, title: str, message: str, 
                           related_object_type: str = None, related_object_id: int = None) -> Notification:
        """
        Create a new notification
        """
        return self.repository.create_notification(
            recipient_id=recipient_id,
            notification_type=notification_type,
            title=title,
            message=message,
            related_object_type=related_object_type,
            related_object_id=related_object_id
        )
    
    def create_system_notification(self, recipient_id: int, title: str, message: str) -> Notification:
        """
        Create a system notification
        """
        return self.create_notification(
            recipient_id=recipient_id,
            notification_type=Notification.NotificationType.SYSTEM,
            title=title,
            message=message
        )
    
    def create_order_placed_notification(self, recipient_id: int, order_id: int, title: str, message: str) -> Notification:
        """
        Create an order placed notification
        """
        return self.create_notification(
            recipient_id=recipient_id,
            notification_type=Notification.NotificationType.ORDER_PLACED,
            title=title,
            message=message,
            related_object_type='Order',
            related_object_id=order_id
        )
    
    def create_order_updated_notification(self, recipient_id: int, order_id: int, title: str, message: str) -> Notification:
        """
        Create an order updated notification
        """
        return self.create_notification(
            recipient_id=recipient_id,
            notification_type=Notification.NotificationType.ORDER_UPDATED,
            title=title,
            message=message,
            related_object_type='Order',
            related_object_id=order_id
        )
    
    def create_product_updated_notification(self, recipient_id: int, product_id: int, title: str, message: str) -> Notification:
        """
        Create a product updated notification
        """
        return self.create_notification(
            recipient_id=recipient_id,
            notification_type=Notification.NotificationType.PRODUCT_UPDATED,
            title=title,
            message=message,
            related_object_type='Product',
            related_object_id=product_id
        )
