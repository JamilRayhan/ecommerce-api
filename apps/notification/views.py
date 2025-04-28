from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Notification
from .serializers import NotificationSerializer
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'is_read']
    ordering_fields = ['created_at']

    def get_queryset(self):
        """
        This view returns a list of all notifications for the currently authenticated user.
        Uses caching to improve performance.
        """
        user = self.request.user
        cache_key = f'user_notifications_{user.id}'

        # Try to get from cache first
        cached_queryset = cache.get(cache_key)
        if cached_queryset is not None:
            return cached_queryset

        # If not in cache, get from database
        queryset = Notification.objects.filter(recipient=user).order_by('-created_at')

        # Store in cache for 5 minutes
        cache.set(cache_key, queryset, 300)

        return queryset

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Get all unread notifications for the current user
        """
        queryset = self.get_queryset().filter(is_read=False)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark a notification as read
        """
        notification = self.get_object()
        notification.is_read = True
        notification.save()

        # Invalidate cache
        cache_key = f'user_notifications_{request.user.id}'
        cache.delete(cache_key)

        return Response({'status': 'notification marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Mark all notifications as read
        """
        self.get_queryset().filter(is_read=False).update(is_read=True)

        # Invalidate cache
        cache_key = f'user_notifications_{request.user.id}'
        cache.delete(cache_key)

        return Response({'status': 'all notifications marked as read'})
