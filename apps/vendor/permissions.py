from rest_framework import permissions
from apps.user.permissions import IsAdmin

class IsVendorOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow vendor owners or admins to access the vendor object
    """
    def has_object_permission(self, request, view, obj):
        # Admin can access any vendor
        if request.user.is_admin():
            return True
        
        # Vendor can only access their own profile
        return obj.user == request.user
