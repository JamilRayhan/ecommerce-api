from rest_framework import serializers
from .models import Product, Category
from apps.vendor.serializers import VendorSerializer

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model
    """
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description')
        read_only_fields = ('slug',)

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model
    """
    vendor = VendorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'vendor', 'category', 'name', 'slug', 'description', 'price', 'stock', 'is_available', 'created_at', 'updated_at')
        read_only_fields = ('slug', 'created_at', 'updated_at')

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating products
    """
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Product
        fields = ('id', 'category_id', 'name', 'description', 'price', 'stock', 'is_available')

    def validate_category_id(self, value):
        try:
            Category.objects.get(pk=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Category does not exist")
        return value

    def validate_price(self, value):
        """
        Validate that the price is positive
        """
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero")
        return value

    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        category = Category.objects.get(pk=category_id)

        user = self.context['request'].user
        vendor = user.vendor_profile

        product = Product.objects.create(
            vendor=vendor,
            category=category,
            **validated_data
        )
        return product

    def update(self, instance, validated_data):
        if 'category_id' in validated_data:
            category_id = validated_data.pop('category_id')
            category = Category.objects.get(pk=category_id)
            instance.category = category

        return super().update(instance, validated_data)
