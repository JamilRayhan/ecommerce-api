from apps.core.repositories import BaseRepository
from .models import Order, OrderItem
from typing import Optional, List, Dict, Any, Union
from django.db.models import Q, QuerySet, Count, Sum, Avg, F
from datetime import datetime, timedelta


class OrderRepository(BaseRepository):
    """
    Repository for Order model
    """
    
    def __init__(self):
        super().__init__(Order)
    
    def get_by_order_number(self, order_number: str) -> Optional[Order]:
        """
        Get an order by order number
        """
        try:
            return self.model_class.objects.get(order_number=order_number)
        except self.model_class.DoesNotExist:
            return None
    
    def get_by_customer_id(self, customer_id: int) -> QuerySet:
        """
        Get orders by customer ID
        """
        return self.model_class.objects.filter(customer_id=customer_id)
    
    def get_by_status(self, status: str) -> QuerySet:
        """
        Get orders by status
        """
        return self.model_class.objects.filter(status=status)
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> QuerySet:
        """
        Get orders by date range
        """
        return self.model_class.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
    
    def get_recent(self, days: int = 30) -> QuerySet:
        """
        Get recent orders
        """
        start_date = datetime.now() - timedelta(days=days)
        return self.get_by_date_range(start_date, datetime.now())
    
    def get_by_vendor_id(self, vendor_id: int) -> QuerySet:
        """
        Get orders containing products from a specific vendor
        """
        return self.model_class.objects.filter(
            items__product__vendor_id=vendor_id
        ).distinct()
    
    def get_with_items(self) -> QuerySet:
        """
        Get orders with items preloaded
        """
        return self.model_class.objects.prefetch_related(
            'items',
            'items__product',
            'items__product__vendor',
            'items__product__category'
        )
    
    def get_with_customer(self) -> QuerySet:
        """
        Get orders with customer preloaded
        """
        return self.model_class.objects.select_related('customer')
    
    def get_with_all_relations(self) -> QuerySet:
        """
        Get orders with all relations preloaded
        """
        return self.get_with_customer().prefetch_related(
            'items',
            'items__product',
            'items__product__vendor',
            'items__product__category'
        )
    
    def get_total_sales(self) -> float:
        """
        Get total sales
        """
        result = self.model_class.objects.aggregate(total=Sum('total_price'))
        return result['total'] or 0
    
    def get_sales_by_period(self, period: str) -> Dict[str, float]:
        """
        Get sales by period (daily, weekly, monthly)
        """
        # Implementation depends on the database being used
        # This is a simplified version
        if period == 'daily':
            days = 30
        elif period == 'weekly':
            days = 90
        else:  # monthly
            days = 365
            
        start_date = datetime.now() - timedelta(days=days)
        orders = self.get_by_date_range(start_date, datetime.now())
        
        # Group by period and sum
        # This is a simplified version
        result = {}
        for order in orders:
            key = order.created_at.strftime('%Y-%m-%d')
            if key not in result:
                result[key] = 0
            result[key] += float(order.total_price)
            
        return result


class OrderItemRepository(BaseRepository):
    """
    Repository for OrderItem model
    """
    
    def __init__(self):
        super().__init__(OrderItem)
    
    def get_by_order_id(self, order_id: int) -> QuerySet:
        """
        Get order items by order ID
        """
        return self.model_class.objects.filter(order_id=order_id)
    
    def get_by_product_id(self, product_id: int) -> QuerySet:
        """
        Get order items by product ID
        """
        return self.model_class.objects.filter(product_id=product_id)
    
    def get_by_vendor_id(self, vendor_id: int) -> QuerySet:
        """
        Get order items by vendor ID
        """
        return self.model_class.objects.filter(product__vendor_id=vendor_id)
    
    def get_with_product(self) -> QuerySet:
        """
        Get order items with product preloaded
        """
        return self.model_class.objects.select_related('product')
    
    def get_with_order(self) -> QuerySet:
        """
        Get order items with order preloaded
        """
        return self.model_class.objects.select_related('order')
    
    def get_with_all_relations(self) -> QuerySet:
        """
        Get order items with all relations preloaded
        """
        return self.model_class.objects.select_related(
            'order',
            'product',
            'product__vendor',
            'product__category'
        )
    
    def get_total_quantity_by_product(self, product_id: int) -> int:
        """
        Get total quantity sold for a product
        """
        result = self.get_by_product_id(product_id).aggregate(total=Sum('quantity'))
        return result['total'] or 0
    
    def get_best_selling_products(self, limit: int = 10) -> QuerySet:
        """
        Get best selling products
        """
        return self.model_class.objects.values(
            'product'
        ).annotate(
            total_quantity=Sum('quantity')
        ).order_by('-total_quantity')[:limit]
