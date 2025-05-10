from rest_framework import permissions
from typing import Any


class BasePermission(permissions.BasePermission):
    """
    Base permission class that all permissions should inherit from.
    Provides common permission functionality.
    
    Implements the Single Responsibility Principle by centralizing common permission functionality.
    """
    
    def has_permission(self, request, view):
        """
        Default implementation returns True.
        Override in subclasses as needed.
        """
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Default implementation returns True.
        Override in subclasses as needed.
        """
        return True


class IsAuthenticated(BasePermission):
    """
    Permission to only allow authenticated users to access the view
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsOwner(BasePermission):
    """
    Permission to only allow owners of an object to access it.
    Assumes the model instance has an `owner` attribute.
    """
    
    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        return obj.owner == request.user


class IsReadOnly(BasePermission):
    """
    Permission to only allow read-only methods
    """
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAdminUser(BasePermission):
    """
    Permission to only allow admin users to access the view
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin()


class IsVendorUser(BasePermission):
    """
    Permission to only allow vendor users to access the view
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_vendor()


class IsCustomerUser(BasePermission):
    """
    Permission to only allow customer users to access the view
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_customer()
