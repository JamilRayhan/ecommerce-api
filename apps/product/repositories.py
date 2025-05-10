from apps.core.repositories import BaseRepository
from .models import Product, Category
from typing import Optional, List, Dict, Any, Union
from django.db.models import Q, QuerySet, Count, Avg, Min, Max


class CategoryRepository(BaseRepository):
    """
    Repository for Category model
    """
    
    def __init__(self):
        super().__init__(Category)
    
    def get_by_slug(self, slug: str) -> Optional[Category]:
        """
        Get a category by slug
        """
        try:
            return self.model_class.objects.get(slug=slug)
        except self.model_class.DoesNotExist:
            return None
    
    def get_by_name(self, name: str) -> Optional[Category]:
        """
        Get a category by name
        """
        try:
            return self.model_class.objects.get(name=name)
        except self.model_class.DoesNotExist:
            return None
    
    def search(self, query: str) -> QuerySet:
        """
        Search categories by name or description
        """
        return self.model_class.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    
    def get_with_product_count(self) -> QuerySet:
        """
        Get all categories with product count
        """
        return self.model_class.objects.annotate(product_count=Count('products'))
    
    def get_active_with_product_count(self) -> QuerySet:
        """
        Get active categories with product count
        """
        return self.get_active().annotate(product_count=Count('products'))


class ProductRepository(BaseRepository):
    """
    Repository for Product model
    """
    
    def __init__(self):
        super().__init__(Product)
    
    def get_by_slug(self, slug: str) -> Optional[Product]:
        """
        Get a product by slug
        """
        try:
            return self.model_class.objects.get(slug=slug)
        except self.model_class.DoesNotExist:
            return None
    
    def get_by_vendor_id(self, vendor_id: int) -> QuerySet:
        """
        Get products by vendor ID
        """
        return self.model_class.objects.filter(vendor_id=vendor_id)
    
    def get_by_category_id(self, category_id: int) -> QuerySet:
        """
        Get products by category ID
        """
        return self.model_class.objects.filter(category_id=category_id)
    
    def get_available(self) -> QuerySet:
        """
        Get available products
        """
        return self.model_class.objects.filter(is_available=True)
    
    def get_available_by_vendor_id(self, vendor_id: int) -> QuerySet:
        """
        Get available products by vendor ID
        """
        return self.get_available().filter(vendor_id=vendor_id)
    
    def get_available_by_category_id(self, category_id: int) -> QuerySet:
        """
        Get available products by category ID
        """
        return self.get_available().filter(category_id=category_id)
    
    def search(self, query: str) -> QuerySet:
        """
        Search products by name or description
        """
        return self.model_class.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    
    def filter_by_price_range(self, min_price: float = None, max_price: float = None) -> QuerySet:
        """
        Filter products by price range
        """
        queryset = self.model_class.objects.all()
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        return queryset
    
    def get_price_stats(self) -> Dict[str, Any]:
        """
        Get price statistics
        """
        stats = self.model_class.objects.aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price')
        )
        return stats
    
    def get_featured(self, limit: int = 10) -> QuerySet:
        """
        Get featured products
        """
        return self.get_available().order_by('-created_at')[:limit]
