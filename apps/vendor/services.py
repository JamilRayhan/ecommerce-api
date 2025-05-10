from apps.core.services import BaseService
from .repositories import VendorRepository
from apps.user.services import UserService
from .models import Vendor
from typing import Optional, List, Dict, Any, Union
from django.db.models import QuerySet


class VendorService(BaseService):
    """
    Service for Vendor model
    """
    
    def __init__(self):
        super().__init__(VendorRepository())
        self.user_service = UserService()
    
    def get_by_user_id(self, user_id: int) -> Optional[Vendor]:
        """
        Get a vendor by user ID
        """
        return self.repository.get_by_user_id(user_id)
    
    def get_by_company_name(self, company_name: str) -> Optional[Vendor]:
        """
        Get a vendor by company name
        """
        return self.repository.get_by_company_name(company_name)
    
    def search(self, query: str) -> QuerySet:
        """
        Search vendors by company name or description
        """
        return self.repository.search(query)
    
    def get_with_product_count(self) -> QuerySet:
        """
        Get all vendors with product count
        """
        return self.repository.get_with_product_count()
    
    def get_active_with_product_count(self) -> QuerySet:
        """
        Get active vendors with product count
        """
        return self.repository.get_active_with_product_count()
    
    def create_vendor(self, user_id: int, **kwargs) -> Vendor:
        """
        Create a vendor for a user
        """
        # Create the vendor
        vendor = self.repository.create_for_user(user_id, **kwargs)
        
        # Update user role to vendor
        self.user_service.change_role(user_id, 'VENDOR')
        
        return vendor
    
    def update_vendor(self, vendor_id: int, **kwargs) -> Optional[Vendor]:
        """
        Update a vendor
        """
        return self.update(vendor_id, **kwargs)
    
    def deactivate_vendor(self, vendor_id: int) -> Optional[Vendor]:
        """
        Deactivate a vendor
        """
        return self.soft_delete(vendor_id)
    
    def activate_vendor(self, vendor_id: int) -> Optional[Vendor]:
        """
        Activate a vendor
        """
        vendor = self.get_by_id(vendor_id)
        if vendor:
            vendor.restore()
            return vendor
        return None
