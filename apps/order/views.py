from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from .permissions import IsCustomerOwnerOrVendorOrAdmin
from apps.user.permissions import IsAdmin, IsVendor, IsCustomer
from django.db import transaction

class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for orders
    """
    queryset = Order.objects.all().order_by('id')
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'updated_at', 'total_price']
    permission_classes = [IsCustomerOwnerOrVendorOrAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()

        # Optimize query with select_related and prefetch_related
        queryset = queryset.select_related('customer')
        queryset = queryset.prefetch_related(
            'items',
            'items__product',
            'items__product__vendor',
            'items__product__category'
        )

        # Filter based on user role
        user = self.request.user

        if user.is_customer():
            # Customers can only see their own orders
            queryset = queryset.filter(customer=user)
        elif user.is_vendor():
            # Vendors can see orders containing their products
            vendor_products = user.vendor_profile.products.all()
            vendor_product_ids = [product.id for product in vendor_products]

            # Find orders that contain any of the vendor's products
            queryset = queryset.filter(
                items__product__id__in=vendor_product_ids
            ).distinct()

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # Add ordering to prevent pagination warnings
        return queryset.order_by('id')

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def update_status(self, request, pk=None):
        """
        Update the status of an order (admin only)
        """
        order = self.get_object()
        status = request.data.get('status')

        if status not in [choice[0] for choice in Order.OrderStatus.choices]:
            return Response(
                {"detail": "Invalid status value"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = status
        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsVendor])
    def vendor_orders(self, request):
        """
        Get orders containing products from the current vendor
        """
        user = request.user
        vendor_products = user.vendor_profile.products.all()
        vendor_product_ids = [product.id for product in vendor_products]

        queryset = Order.objects.filter(
            items__product__id__in=vendor_product_ids
        ).distinct()

        queryset = queryset.select_related('customer')
        queryset = queryset.prefetch_related(
            'items',
            'items__product',
            'items__product__vendor',
            'items__product__category'
        )

        # Add ordering to prevent pagination warnings
        queryset = queryset.order_by('id')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)
