from rest_framework import serializers
from .models import Order, OrderItem
from apps.product.serializers import ProductSerializer
from apps.product.models import Product
from apps.user.serializers import UserProfileSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the OrderItem model
    """
    product = ProductSerializer(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'price', 'total_price')
        read_only_fields = ('price',)

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model
    """
    customer = UserProfileSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'order_number', 'customer', 'status', 'total_price', 'shipping_address', 'created_at', 'updated_at', 'items')
        read_only_fields = ('order_number', 'created_at', 'updated_at')

class OrderItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating order items
    """
    product_id = serializers.IntegerField()
    
    class Meta:
        model = OrderItem
        fields = ('product_id', 'quantity')
    
    def validate_product_id(self, value):
        try:
            product = Product.objects.get(pk=value)
            if not product.is_available or product.stock <= 0:
                raise serializers.ValidationError("Product is not available")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist")
        return value

class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating orders
    """
    items = OrderItemCreateSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ('shipping_address', 'items')
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        # Calculate total price
        total_price = 0
        for item_data in items_data:
            product = Product.objects.get(pk=item_data['product_id'])
            total_price += product.price * item_data['quantity']
        
        # Create order
        order = Order.objects.create(
            customer=user,
            total_price=total_price,
            **validated_data
        )
        
        # Create order items
        for item_data in items_data:
            product = Product.objects.get(pk=item_data['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price=product.price
            )
            
            # Update product stock
            product.stock -= item_data['quantity']
            product.save()
        
        return order
