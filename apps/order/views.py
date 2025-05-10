from rest_framework import permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer
from .permissions import IsCustomerOwnerOrVendorOrAdmin
from apps.user.permissions import IsAdmin, IsVendor, IsCustomer
from .services import OrderService
from apps.core.views import BaseModelViewSet
from datetime import datetime

class OrderViewSet(BaseModelViewSet):
    """
    API endpoint for orders
    """
    serializer_class = OrderSerializer
    service_class = OrderService
    serializer_classes = {
        'create': OrderCreateSerializer,
    }
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'updated_at', 'total_price']
    permission_classes = [IsCustomerOwnerOrVendorOrAdmin]

    def get_queryset(self):
        service = self.get_service()

        # Get orders with all relations
        queryset = service.get_with_all_relations()

        # Filter based on user role
        user = self.request.user

        if user.is_customer():
            # Customers can only see their own orders
            queryset = service.get_by_customer_id(user.id)
        elif user.is_vendor():
            # Vendors can see orders containing their products
            queryset = service.get_by_vendor_id(user.vendor_profile.id)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            queryset = service.get_by_date_range(start_date, end_date)

        return queryset

    def perform_create(self, serializer):
        service = self.get_service()
        validated_data = serializer.validated_data

        # Extract items data
        items_data = validated_data.pop('items')

        # Create order for the current user
        instance = service.create_order(
            customer_id=self.request.user.id,
            shipping_address=validated_data['shipping_address'],
            items=items_data
        )

        serializer.instance = instance

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def update_status(self, request, pk=None):
        """
        Update the status of an order (admin only)
        """
        service = self.get_service()
        status_value = request.data.get('status')

        # Update order status
        order = service.update_order_status(pk, status_value)

        if order:
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        else:
            return Response(
                {"detail": "Invalid status value"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], permission_classes=[IsVendor])
    def vendor_orders(self, request):
        """
        Get orders containing products from the current vendor
        """
        service = self.get_service()
        queryset = service.get_by_vendor_id(request.user.vendor_profile.id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
