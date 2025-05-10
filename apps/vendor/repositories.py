from apps.core.repositories import BaseRepository
from .models import Vendor
from typing import Optional, List, Dict, Any, Union
from django.db.models import Q, QuerySet, Count, Avg


class VendorRepository(BaseRepository):
    """
    Repository for Vendor model
    """
    
    def __init__(self):
        super().__init__(Vendor)
    
    def get_by_user_id(self, user_id: int) -> Optional[Vendor]:
        """
        Get a vendor by user ID
        """
        try:
            return self.model_class.objects.get(user_id=user_id)
        except self.model_class.DoesNotExist:
            return None
    
    def get_by_company_name(self, company_name: str) -> Optional[Vendor]:
        """
        Get a vendor by company name
        """
        try:
            return self.model_class.objects.get(company_name=company_name)
        except self.model_class.DoesNotExist:
            return None
    
    def search(self, query: str) -> QuerySet:
        """
        Search vendors by company name or description
        """
        return self.model_class.objects.filter(
            Q(company_name__icontains=query) |
            Q(description__icontains=query)
        )
    
    def get_with_product_count(self) -> QuerySet:
        """
        Get all vendors with product count
        """
        return self.model_class.objects.annotate(product_count=Count('products'))
    
    def get_active_with_product_count(self) -> QuerySet:
        """
        Get active vendors with product count
        """
        return self.get_active().annotate(product_count=Count('products'))
    
    def create_for_user(self, user_id: int, **kwargs) -> Vendor:
        """
        Create a vendor for a user
        """
        return self.model_class.objects.create(user_id=user_id, **kwargs)
