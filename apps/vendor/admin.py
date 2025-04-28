from django.contrib import admin
from .models import Vendor

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('company_name', 'user__username', 'user__email')
    raw_id_fields = ('user',)
