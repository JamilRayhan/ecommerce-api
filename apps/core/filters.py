from django_filters import rest_framework as filters
from django.db.models import Q
from typing import Any, Dict, List


class BaseFilterSet(filters.FilterSet):
    """
    Base filter set class that all filter sets should inherit from.
    Provides common filtering functionality.
    
    Implements the Single Responsibility Principle by centralizing common filter functionality.
    """
    
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    is_active = filters.BooleanFilter(field_name='is_active')
    
    class Meta:
        abstract = True


class SearchFilter(filters.CharFilter):
    """
    Custom filter for performing text search across multiple fields
    """
    
    def __init__(self, search_fields=None, *args, **kwargs):
        self.search_fields = search_fields or []
        super().__init__(*args, **kwargs)
    
    def filter(self, qs, value):
        if not value:
            return qs
        
        q_objects = Q()
        for field in self.search_fields:
            q_objects |= Q(**{f"{field}__icontains": value})
        
        return qs.filter(q_objects)


class DateRangeFilter(filters.DateFromToRangeFilter):
    """
    Custom filter for date ranges
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def filter(self, qs, value):
        if not value:
            return qs
        
        lookup = '%s__range' % self.field_name
        start = value.start
        stop = value.stop
        
        if start and stop:
            return qs.filter(**{lookup: (start, stop)})
        
        if start:
            return qs.filter(**{'%s__gte' % self.field_name: start})
        
        if stop:
            return qs.filter(**{'%s__lte' % self.field_name: stop})
        
        return qs
