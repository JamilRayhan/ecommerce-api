from rest_framework import permissions
from apps.user.permissions import IsAdmin

class IsCustomerOwnerOrVendorOrAdmin(permissions.BasePermission):
    """
    Permission to allow:
    - Customers to view and create their own orders
    - Vendors to view orders containing their products
    - Admins to view all orders
    """
    def has_permission(self, request, view):
        # Only authenticated users can access orders
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin can access any order
        if request.user.is_admin():
            return True
        
        # Customer can only access their own orders
        if request.user.is_customer():
            return obj.customer == request.user
        
        # Vendor can access orders containing their products
        if request.user.is_vendor():
            # Check if any order item contains a product from this vendor
            vendor_products = request.user.vendor_profile.products.all()
            vendor_product_ids = [product.id for product in vendor_products]
            
            # Check if any order item has a product from this vendor
            for item in obj.items.all():
                if item.product.id in vendor_product_ids:
                    return True
            
        return False
