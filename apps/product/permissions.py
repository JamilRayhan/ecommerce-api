from rest_framework import permissions
from apps.user.permissions import IsAdmin

class IsVendorOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow vendors who own the product to edit it
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only authenticated vendors or admins can create products
        return request.user and request.user.is_authenticated and (
            request.user.is_vendor() or request.user.is_admin()
        )
    
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Admin can edit any product
        if request.user.is_admin():
            return True
        
        # Vendor can only edit their own products
        return request.user.is_vendor() and obj.vendor.user == request.user
