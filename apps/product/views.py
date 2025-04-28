from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category
from .serializers import ProductSerializer, ProductCreateUpdateSerializer, CategorySerializer
from .permissions import IsVendorOwnerOrReadOnly
from apps.user.permissions import IsAdmin

class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for product categories
    """
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for products
    """
    queryset = Product.objects.all().order_by('id')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_available', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    permission_classes = [IsVendorOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()

        # Optimize query with select_related and prefetch_related
        queryset = queryset.select_related('vendor', 'vendor__user', 'category')

        # Filter by vendor if requested
        vendor_id = self.request.query_params.get('vendor_id')
        if vendor_id:
            queryset = queryset.filter(vendor_id=vendor_id)

        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # For vendor users, only show their products
        user = self.request.user
        if user.is_authenticated and user.is_vendor() and self.action == 'list':
            if not self.request.query_params.get('all'):
                queryset = queryset.filter(vendor__user=user)

        # Add ordering to prevent pagination warnings
        return queryset.order_by('id')

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured products
        """
        # Use the get_queryset method which already includes ordering
        queryset = self.get_queryset().filter(is_available=True)[:10]
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)
