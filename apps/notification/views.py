from rest_framework import permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import NotificationSerializer
from .services import NotificationService
from apps.core.views import BaseReadOnlyViewSet

class NotificationViewSet(BaseReadOnlyViewSet):
    """
    API endpoint for notifications
    """
    serializer_class = NotificationSerializer
    service_class = NotificationService
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'is_read']
    ordering_fields = ['created_at']

    def get_queryset(self):
        """
        This view returns a list of all notifications for the currently authenticated user.
        Uses caching to improve performance.
        """
        service = self.get_service()
        return service.get_by_recipient_id(self.request.user.id)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Get all unread notifications for the current user
        """
        service = self.get_service()
        queryset = service.get_unread_by_recipient_id(request.user.id)

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
        service = self.get_service()

        # First check if the notification belongs to the current user
        notification = service.get_by_id(pk)
        if not notification or notification.recipient != request.user:
            return Response(
                {"detail": "Notification not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        notification = service.mark_as_read(pk)
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Mark all notifications as read
        """
        service = self.get_service()
        count = service.mark_all_as_read(request.user.id)

        return Response({
            'status': 'all notifications marked as read',
            'count': count
        })
