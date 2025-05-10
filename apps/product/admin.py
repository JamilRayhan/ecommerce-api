from django.contrib import admin
from apps.core.admin import BaseModelAdmin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(BaseModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(BaseModelAdmin):
    list_display = ('name', 'vendor', 'category', 'price', 'stock', 'is_available')
    list_filter = ('is_available', 'category', 'vendor')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('vendor', 'category')
