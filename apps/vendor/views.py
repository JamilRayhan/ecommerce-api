from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg
from .models import Vendor
from .serializers import VendorSerializer, VendorCreateSerializer
from .permissions import IsVendorOwnerOrAdmin
from apps.user.permissions import IsAdmin, IsVendor

class VendorViewSet(viewsets.ModelViewSet):
    """
    API endpoint for vendors
    """
    queryset = Vendor.objects.all().order_by('id')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company_name', 'description']
    ordering_fields = ['company_name', 'created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return VendorCreateSerializer
        return VendorSerializer

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
        queryset = Vendor.objects.all()

        # Optimize query with select_related and prefetch_related
        queryset = queryset.select_related('user')

        # Add product count annotation
        queryset = queryset.annotate(product_count=Count('products'))

        # Filter for non-admin users
        user = self.request.user
        if not user.is_admin():
            queryset = queryset.filter(is_active=True)

        # Add ordering to prevent pagination warnings
        return queryset.order_by('id')

    @action(detail=False, methods=['get'], permission_classes=[IsVendor])
    def me(self, request):
        """
        Get the current vendor's profile
        """
        try:
            vendor = request.user.vendor_profile
            serializer = VendorSerializer(vendor)
            return Response(serializer.data)
        except Vendor.DoesNotExist:
            return Response({"detail": "Vendor profile not found"}, status=404)

    def perform_create(self, serializer):
        serializer.save()
