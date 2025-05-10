from apps.core.services import BaseService
from .repositories import OrderRepository, OrderItemRepository
from apps.product.services import ProductService
from .models import Order, OrderItem
from typing import Optional, List, Dict, Any, Union
from django.db.models import QuerySet
from datetime import datetime, timedelta
from django.db import transaction


class OrderItemService(BaseService):
    """
    Service for OrderItem model
    """
    
    def __init__(self):
        super().__init__(OrderItemRepository())
        self.product_service = ProductService()
    
    def get_by_order_id(self, order_id: int) -> QuerySet:
        """
        Get order items by order ID
        """
        return self.repository.get_by_order_id(order_id)
    
    def get_by_product_id(self, product_id: int) -> QuerySet:
        """
        Get order items by product ID
        """
        return self.repository.get_by_product_id(product_id)
    
    def get_by_vendor_id(self, vendor_id: int) -> QuerySet:
        """
        Get order items by vendor ID
        """
        return self.repository.get_by_vendor_id(vendor_id)
    
    def get_with_product(self) -> QuerySet:
        """
        Get order items with product preloaded
        """
        return self.repository.get_with_product()
    
    def get_with_order(self) -> QuerySet:
        """
        Get order items with order preloaded
        """
        return self.repository.get_with_order()
    
    def get_with_all_relations(self) -> QuerySet:
        """
        Get order items with all relations preloaded
        """
        return self.repository.get_with_all_relations()
    
    def get_total_quantity_by_product(self, product_id: int) -> int:
        """
        Get total quantity sold for a product
        """
        return self.repository.get_total_quantity_by_product(product_id)
    
    def get_best_selling_products(self, limit: int = 10) -> QuerySet:
        """
        Get best selling products
        """
        return self.repository.get_best_selling_products(limit)
    
    def create_order_item(self, order_id: int, product_id: int, quantity: int) -> OrderItem:
        """
        Create a new order item
        """
        # Get the product
        product = self.product_service.get_by_id(product_id)
        
        # Create the order item
        order_item = self.create(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price=product.price
        )
        
        # Update product stock
        self.product_service.update_stock(product_id, -quantity)
        
        return order_item


class OrderService(BaseService):
    """
    Service for Order model
    """
    
    def __init__(self):
        super().__init__(OrderRepository())
        self.order_item_service = OrderItemService()
    
    def get_by_order_number(self, order_number: str) -> Optional[Order]:
        """
        Get an order by order number
        """
        return self.repository.get_by_order_number(order_number)
    
    def get_by_customer_id(self, customer_id: int) -> QuerySet:
        """
        Get orders by customer ID
        """
        return self.repository.get_by_customer_id(customer_id)
    
    def get_by_status(self, status: str) -> QuerySet:
        """
        Get orders by status
        """
        return self.repository.get_by_status(status)
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> QuerySet:
        """
        Get orders by date range
        """
        return self.repository.get_by_date_range(start_date, end_date)
    
    def get_recent(self, days: int = 30) -> QuerySet:
        """
        Get recent orders
        """
        return self.repository.get_recent(days)
    
    def get_by_vendor_id(self, vendor_id: int) -> QuerySet:
        """
        Get orders containing products from a specific vendor
        """
        return self.repository.get_by_vendor_id(vendor_id)
    
    def get_with_items(self) -> QuerySet:
        """
        Get orders with items preloaded
        """
        return self.repository.get_with_items()
    
    def get_with_customer(self) -> QuerySet:
        """
        Get orders with customer preloaded
        """
        return self.repository.get_with_customer()
    
    def get_with_all_relations(self) -> QuerySet:
        """
        Get orders with all relations preloaded
        """
        return self.repository.get_with_all_relations()
    
    def get_total_sales(self) -> float:
        """
        Get total sales
        """
        return self.repository.get_total_sales()
    
    def get_sales_by_period(self, period: str) -> Dict[str, float]:
        """
        Get sales by period (daily, weekly, monthly)
        """
        return self.repository.get_sales_by_period(period)
    
    @transaction.atomic
    def create_order(self, customer_id: int, shipping_address: str, items: List[Dict[str, Any]]) -> Order:
        """
        Create a new order with items
        """
        # Calculate total price
        total_price = 0
        for item in items:
            product = self.product_service.get_by_id(item['product_id'])
            total_price += product.price * item['quantity']
        
        # Create the order
        order = self.create(
            customer_id=customer_id,
            shipping_address=shipping_address,
            total_price=total_price,
            status=Order.OrderStatus.PENDING
        )
        
        # Create order items
        for item in items:
            self.order_item_service.create_order_item(
                order_id=order.id,
                product_id=item['product_id'],
                quantity=item['quantity']
            )
        
        return order
    
    def update_order_status(self, order_id: int, status: str) -> Optional[Order]:
        """
        Update an order's status
        """
        if status not in [choice[0] for choice in Order.OrderStatus.choices]:
            return None
        return self.update(order_id, status=status)
    
    def cancel_order(self, order_id: int) -> Optional[Order]:
        """
        Cancel an order
        """
        return self.update_order_status(order_id, Order.OrderStatus.CANCELLED)
