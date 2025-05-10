from rest_framework import serializers
from typing import Dict, Any, Type
from django.db.models import Model


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Base serializer class that all model serializers should inherit from.
    Provides common serialization functionality.
    
    Implements the Single Responsibility Principle by centralizing common serializer functionality.
    """
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform common validation for all serializers
        """
        # Add common validation logic here
        return super().validate(attrs)
    
    @classmethod
    def setup_eager_loading(cls, queryset):
        """
        Perform necessary eager loading of data to avoid N+1 selects
        To be overridden by child classes
        """
        return queryset


class BaseCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Base serializer for create/update operations.
    Separates read and write operations for better adherence to SRP.
    """
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform common validation for create/update serializers
        """
        # Add common validation logic here
        return super().validate(attrs)


class BaseReadOnlySerializer(serializers.ModelSerializer):
    """
    Base serializer for read-only operations.
    Separates read and write operations for better adherence to SRP.
    """
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    @classmethod
    def setup_eager_loading(cls, queryset):
        """
        Perform necessary eager loading of data to avoid N+1 selects
        To be overridden by child classes
        """
        return queryset
