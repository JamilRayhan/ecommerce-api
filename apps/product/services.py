from apps.core.services import BaseService
from .repositories import ProductRepository, CategoryRepository
from .models import Product, Category
from typing import Optional, List, Dict, Any, Union
from django.db.models import QuerySet


class CategoryService(BaseService):
    """
    Service for Category model
    """
    
    def __init__(self):
        super().__init__(CategoryRepository())
    
    def get_by_slug(self, slug: str) -> Optional[Category]:
        """
        Get a category by slug
        """
        return self.repository.get_by_slug(slug)
    
    def get_by_name(self, name: str) -> Optional[Category]:
        """
        Get a category by name
        """
        return self.repository.get_by_name(name)
    
    def search(self, query: str) -> QuerySet:
        """
        Search categories by name or description
        """
        return self.repository.search(query)
    
    def get_with_product_count(self) -> QuerySet:
        """
        Get all categories with product count
        """
        return self.repository.get_with_product_count()
    
    def get_active_with_product_count(self) -> QuerySet:
        """
        Get active categories with product count
        """
        return self.repository.get_active_with_product_count()
    
    def create_category(self, **kwargs) -> Category:
        """
        Create a new category
        """
        return self.create(**kwargs)
    
    def update_category(self, category_id: int, **kwargs) -> Optional[Category]:
        """
        Update a category
        """
        return self.update(category_id, **kwargs)
    
    def delete_category(self, category_id: int) -> bool:
        """
        Delete a category
        """
        return self.delete(category_id)


class ProductService(BaseService):
    """
    Service for Product model
    """
    
    def __init__(self):
        super().__init__(ProductRepository())
    
    def get_by_slug(self, slug: str) -> Optional[Product]:
        """
        Get a product by slug
        """
        return self.repository.get_by_slug(slug)
    
    def get_by_vendor_id(self, vendor_id: int) -> QuerySet:
        """
        Get products by vendor ID
        """
        return self.repository.get_by_vendor_id(vendor_id)
    
    def get_by_category_id(self, category_id: int) -> QuerySet:
        """
        Get products by category ID
        """
        return self.repository.get_by_category_id(category_id)
    
    def get_available(self) -> QuerySet:
        """
        Get available products
        """
        return self.repository.get_available()
    
    def get_available_by_vendor_id(self, vendor_id: int) -> QuerySet:
        """
        Get available products by vendor ID
        """
        return self.repository.get_available_by_vendor_id(vendor_id)
    
    def get_available_by_category_id(self, category_id: int) -> QuerySet:
        """
        Get available products by category ID
        """
        return self.repository.get_available_by_category_id(category_id)
    
    def search(self, query: str) -> QuerySet:
        """
        Search products by name or description
        """
        return self.repository.search(query)
    
    def filter_by_price_range(self, min_price: float = None, max_price: float = None) -> QuerySet:
        """
        Filter products by price range
        """
        return self.repository.filter_by_price_range(min_price, max_price)
    
    def get_price_stats(self) -> Dict[str, Any]:
        """
        Get price statistics
        """
        return self.repository.get_price_stats()
    
    def get_featured(self, limit: int = 10) -> QuerySet:
        """
        Get featured products
        """
        return self.repository.get_featured(limit)
    
    def create_product(self, vendor_id: int, category_id: int, **kwargs) -> Product:
        """
        Create a new product
        """
        return self.create(vendor_id=vendor_id, category_id=category_id, **kwargs)
    
    def update_product(self, product_id: int, **kwargs) -> Optional[Product]:
        """
        Update a product
        """
        return self.update(product_id, **kwargs)
    
    def update_stock(self, product_id: int, quantity: int) -> Optional[Product]:
        """
        Update product stock
        """
        product = self.get_by_id(product_id)
        if product:
            product.stock += quantity
            product.save(update_fields=['stock', 'updated_at'])
            return product
        return None
    
    def mark_as_available(self, product_id: int) -> Optional[Product]:
        """
        Mark a product as available
        """
        return self.update(product_id, is_available=True)
    
    def mark_as_unavailable(self, product_id: int) -> Optional[Product]:
        """
        Mark a product as unavailable
        """
        return self.update(product_id, is_available=False)
