import logging
from typing import Any, Dict, List, Optional, Union
from django.db.models import QuerySet
from django.core.cache import cache
from django.conf import settings
from functools import wraps
import time
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name
    """
    return logging.getLogger(name)


def cache_result(timeout: int = 300):
    """
    Decorator to cache the result of a function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key based on function name and arguments
            key_parts = [func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            cache_key = ":".join(key_parts)

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # If not in cache, call the function
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result, timeout)

            return result
        return wrapper
    return decorator


def measure_execution_time(func):
    """
    Decorator to measure the execution time of a function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"Function {func.__name__} took {execution_time:.4f} seconds to execute")
        return result
    return wrapper


def paginate_queryset(queryset: QuerySet, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """
    Paginate a queryset
    """
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    data = list(queryset[start:end])

    return {
        'data': data,
        'page': page,
        'page_size': page_size,
        'total': total,
        'total_pages': (total + page_size - 1) // page_size
    }


def filter_queryset(queryset: QuerySet, filters: Dict[str, Any]) -> QuerySet:
    """
    Apply filters to a queryset
    """
    valid_filters = {k: v for k, v in filters.items() if v is not None}
    return queryset.filter(**valid_filters)


def get_object_or_none(queryset: QuerySet, **kwargs) -> Optional[Any]:
    """
    Get an object from a queryset or return None if it doesn't exist
    """
    try:
        return queryset.get(**kwargs)
    except queryset.model.DoesNotExist:
        return None


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # If response is None, there was an unhandled exception
    if response is None:
        logger.exception(exc)
        return Response(
            {'detail': 'A server error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Add more context to the response
    if isinstance(response.data, dict):
        # Add request info
        request = context.get('request')
        if request:
            response.data['path'] = request.path
            response.data['method'] = request.method

    return response
