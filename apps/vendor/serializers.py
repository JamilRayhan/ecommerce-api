from rest_framework import serializers
from .models import Vendor
from apps.user.serializers import UserProfileSerializer

class VendorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Vendor model
    """
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Vendor
        fields = ('id', 'user', 'company_name', 'description', 'address', 'created_at', 'updated_at', 'is_active')
        read_only_fields = ('created_at', 'updated_at')

class VendorCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a vendor
    """
    class Meta:
        model = Vendor
        fields = ('id', 'company_name', 'description', 'address', 'is_active')
    
    def create(self, validated_data):
        user = self.context['request'].user
        vendor = Vendor.objects.create(user=user, **validated_data)
        
        # Update user role to vendor
        user.role = user.Role.VENDOR
        user.save()
        
        return vendor
