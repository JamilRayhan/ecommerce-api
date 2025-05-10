from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class Vendor(BaseModel):
    """
    Vendor model representing a seller in the e-commerce system
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_profile'
    )
    company_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    address = models.TextField()

    def __str__(self):
        return self.company_name
