import time
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest, HttpResponse
from typing import Callable, Any

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests and responses
    """
    
    def process_request(self, request: HttpRequest) -> None:
        """
        Process the request and log it
        """
        request.start_time = time.time()
        
        # Log the request
        logger.info(f"Request: {request.method} {request.path}")
        
        # Log request headers
        headers = {k: v for k, v in request.META.items() if k.startswith('HTTP_')}
        logger.debug(f"Request headers: {headers}")
        
        # Log request body for non-GET requests
        if request.method != 'GET' and request.body:
            try:
                body = json.loads(request.body)
                # Mask sensitive data
                if 'password' in body:
                    body['password'] = '******'
                if 'password2' in body:
                    body['password2'] = '******'
                logger.debug(f"Request body: {body}")
            except json.JSONDecodeError:
                logger.debug(f"Request body: {request.body}")
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Process the response and log it
        """
        # Calculate request duration
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(f"Response: {request.method} {request.path} - {response.status_code} in {duration:.2f}s")
        else:
            logger.info(f"Response: {request.method} {request.path} - {response.status_code}")
        
        # Log response body for non-success responses
        if response.status_code >= 400:
            try:
                body = json.loads(response.content)
                logger.debug(f"Response body: {body}")
            except json.JSONDecodeError:
                logger.debug(f"Response body: {response.content}")
        
        return response


class ExceptionLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all exceptions
    """
    
    def process_exception(self, request: HttpRequest, exception: Exception) -> None:
        """
        Process the exception and log it
        """
        logger.exception(f"Exception during processing of request: {request.method} {request.path}")
        logger.exception(exception)
