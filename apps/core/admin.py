from django.contrib import admin
from django.db.models import Model
from typing import List, Type, Dict, Any, Optional


class BaseModelAdmin(admin.ModelAdmin):
    """
    Base admin class that all model admins should inherit from.
    Provides common admin functionality.
    
    Implements the Single Responsibility Principle by centralizing common admin functionality.
    """
    
    list_display = ('id', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('id',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def get_readonly_fields(self, request, obj=None):
        """
        Make certain fields readonly when editing an existing object
        """
        if obj:  # editing an existing object
            return self.readonly_fields + ('id',)
        return self.readonly_fields
    
    def get_list_display(self, request):
        """
        Get the list of fields to display in the admin list view
        """
        return self.list_display
    
    def get_list_filter(self, request):
        """
        Get the list of fields to filter by in the admin list view
        """
        return self.list_filter
    
    def get_search_fields(self, request):
        """
        Get the list of fields to search by in the admin list view
        """
        return self.search_fields
