from rest_framework import permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import ProductSerializer, ProductCreateUpdateSerializer, CategorySerializer
from .permissions import IsVendorOwnerOrReadOnly
from apps.user.permissions import IsAdmin
from .services import CategoryService, ProductService
from apps.core.views import BaseModelViewSet

class CategoryViewSet(BaseModelViewSet):
    """
    API endpoint for product categories
    """
    serializer_class = CategorySerializer
    service_class = CategoryService
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

class ProductViewSet(BaseModelViewSet):
    """
    API endpoint for products
    """
    serializer_class = ProductSerializer
    service_class = ProductService
    serializer_classes = {
        'create': ProductCreateUpdateSerializer,
        'update': ProductCreateUpdateSerializer,
        'partial_update': ProductCreateUpdateSerializer,
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_available', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    permission_classes = [IsVendorOwnerOrReadOnly]

    def get_queryset(self):
        service = self.get_service()
        queryset = service.get_all()

        # Filter by vendor if requested
        vendor_id = self.request.query_params.get('vendor_id')
        if vendor_id:
            queryset = service.get_by_vendor_id(vendor_id)

        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price or max_price:
            queryset = service.filter_by_price_range(min_price, max_price)

        # For vendor users, only show their products
        user = self.request.user
        if user.is_authenticated and user.is_vendor() and self.action == 'list':
            if not self.request.query_params.get('all'):
                queryset = service.get_by_vendor_id(user.vendor_profile.id)

        return queryset

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def featured(self, request):
        """
        Get featured products
        """
        service = self.get_service()
        queryset = service.get_featured(10)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        service = self.get_service()
        validated_data = serializer.validated_data

        # Get category_id from validated data
        category_id = validated_data.pop('category_id')

        # Create product for the current vendor
        instance = service.create_product(
            vendor_id=self.request.user.vendor_profile.id,
            category_id=category_id,
            **validated_data
        )

        serializer.instance = instance
