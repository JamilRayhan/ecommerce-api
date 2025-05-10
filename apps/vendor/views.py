from rest_framework import permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import VendorSerializer, VendorCreateSerializer
from .permissions import IsVendorOwnerOrAdmin
from apps.user.permissions import IsAdmin, IsVendor
from .services import VendorService
from apps.core.views import BaseModelViewSet

class VendorViewSet(BaseModelViewSet):
    """
    API endpoint for vendors
    """
    serializer_class = VendorSerializer
    service_class = VendorService
    serializer_classes = {
        'create': VendorCreateSerializer,
    }
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company_name', 'description']
    ordering_fields = ['company_name', 'created_at']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsVendorOwnerOrAdmin]
        elif self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        service = self.get_service()
        queryset = service.get_with_product_count()

        # Filter for non-admin users
        user = self.request.user
        if not user.is_admin():
            queryset = queryset.filter(is_active=True)

        return queryset

    @action(detail=False, methods=['get'], permission_classes=[IsVendor])
    def me(self, request):
        """
        Get the current vendor's profile
        """
        service = self.get_service()
        vendor = service.get_by_user_id(request.user.id)

        if vendor:
            serializer = self.get_serializer(vendor)
            return Response(serializer.data)
        else:
            return Response({"detail": "Vendor profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def perform_create(self, serializer):
        service = self.get_service()
        validated_data = serializer.validated_data

        # Create vendor for the current user
        instance = service.create_vendor(
            user_id=self.request.user.id,
            **validated_data
        )

        serializer.instance = instance
