from django.db import models
from django.utils import timezone
from model_utils import FieldTracker


class BaseModel(models.Model):
    """
    Base model class that all models should inherit from.
    Provides common fields and functionality.
    
    Implements the Single Responsibility Principle by centralizing common model functionality.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Track changes to fields
    tracker = FieldTracker()
    
    class Meta:
        abstract = True
        
    def soft_delete(self):
        """
        Soft delete the model instance by setting is_active to False
        """
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])
        
    def restore(self):
        """
        Restore a soft-deleted model instance
        """
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])
        
    def update(self, **kwargs):
        """
        Update model instance with the given keyword arguments
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()
