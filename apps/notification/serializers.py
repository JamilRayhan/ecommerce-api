from rest_framework import serializers
from .models import Notification
from apps.user.serializers import UserProfileSerializer

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model
    """
    recipient = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = ('id', 'recipient', 'notification_type', 'title', 'message', 
                  'related_object_id', 'related_object_type', 'is_read', 'created_at')
        read_only_fields = ('id', 'recipient', 'notification_type', 'title', 'message', 
                           'related_object_id', 'related_object_type', 'created_at')
