from django.contrib import admin
from apps.core.admin import BaseModelAdmin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('product',)
    extra = 0

@admin.register(Order)
class OrderAdmin(BaseModelAdmin):
    list_display = ('order_number', 'customer', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'customer__username', 'customer__email')
    raw_id_fields = ('customer',)
    inlines = [OrderItemInline]
    readonly_fields = ('order_number',)

@admin.register(OrderItem)
class OrderItemAdmin(BaseModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order__status',)
    search_fields = ('order__order_number', 'product__name')
    raw_id_fields = ('order', 'product')
