from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from typing import Dict, Any, List


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class for API results
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data: List[Dict[str, Any]]) -> Response:
        """
        Return a paginated response with additional metadata
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination class for large result sets
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500
    
    def get_paginated_response(self, data: List[Dict[str, Any]]) -> Response:
        """
        Return a paginated response with additional metadata
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })


class SmallResultsSetPagination(PageNumberPagination):
    """
    Pagination class for small result sets
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20
    
    def get_paginated_response(self, data: List[Dict[str, Any]]) -> Response:
        """
        Return a paginated response with additional metadata
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })
