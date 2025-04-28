from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Permission to only allow admin users to access the view
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin()

class IsVendor(permissions.BasePermission):
    """
    Permission to only allow vendor users to access the view
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_vendor()

class IsCustomer(permissions.BasePermission):
    """
    Permission to only allow customer users to access the view
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_customer()

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow owners of an object or admins to access it
    """
    def has_permission(self, request, view):
        # Allow authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin can access any object
        if request.user.is_admin():
            return True

        # For User objects, check if the user is accessing their own profile
        if obj == request.user:
            return True

        # Check if the object has a user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # Check if the object has a customer attribute
        if hasattr(obj, 'customer'):
            return obj.customer == request.user

        return False
