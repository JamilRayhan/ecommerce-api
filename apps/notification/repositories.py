from apps.core.repositories import BaseRepository
from .models import Notification
from typing import Optional, List, Dict, Any, Union
from django.db.models import Q, QuerySet
from django.core.cache import cache


class NotificationRepository(BaseRepository):
    """
    Repository for Notification model
    """
    
    def __init__(self):
        super().__init__(Notification)
    
    def get_by_recipient_id(self, recipient_id: int) -> QuerySet:
        """
        Get notifications by recipient ID
        """
        cache_key = f'user_notifications_{recipient_id}'
        cached_queryset = cache.get(cache_key)
        
        if cached_queryset is not None:
            return cached_queryset
        
        queryset = self.model_class.objects.filter(recipient_id=recipient_id).order_by('-created_at')
        cache.set(cache_key, queryset, 300)  # Cache for 5 minutes
        
        return queryset
    
    def get_unread_by_recipient_id(self, recipient_id: int) -> QuerySet:
        """
        Get unread notifications by recipient ID
        """
        return self.get_by_recipient_id(recipient_id).filter(is_read=False)
    
    def get_by_type(self, notification_type: str) -> QuerySet:
        """
        Get notifications by type
        """
        return self.model_class.objects.filter(notification_type=notification_type)
    
    def get_by_related_object(self, object_type: str, object_id: int) -> QuerySet:
        """
        Get notifications by related object
        """
        return self.model_class.objects.filter(
            related_object_type=object_type,
            related_object_id=object_id
        )
    
    def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        """
        Mark a notification as read
        """
        notification = self.get_by_id(notification_id)
        if notification:
            notification.is_read = True
            notification.save(update_fields=['is_read', 'updated_at'])
            
            # Invalidate cache
            cache_key = f'user_notifications_{notification.recipient_id}'
            cache.delete(cache_key)
            
            return notification
        return None
    
    def mark_all_as_read(self, recipient_id: int) -> int:
        """
        Mark all notifications for a recipient as read
        """
        count = self.get_unread_by_recipient_id(recipient_id).update(is_read=True)
        
        # Invalidate cache
        cache_key = f'user_notifications_{recipient_id}'
        cache.delete(cache_key)
        
        return count
    
    def create_notification(self, recipient_id: int, notification_type: str, title: str, message: str, 
                           related_object_type: str = None, related_object_id: int = None) -> Notification:
        """
        Create a new notification
        """
        notification = self.create(
            recipient_id=recipient_id,
            notification_type=notification_type,
            title=title,
            message=message,
            related_object_type=related_object_type,
            related_object_id=related_object_id
        )
        
        # Invalidate cache
        cache_key = f'user_notifications_{recipient_id}'
        cache.delete(cache_key)
        
        return notification
