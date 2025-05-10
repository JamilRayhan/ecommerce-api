from rest_framework.exceptions import APIException
from rest_framework import status


class BaseAPIException(APIException):
    """
    Base exception class for API exceptions.
    All custom API exceptions should inherit from this class.
    
    Implements the Single Responsibility Principle by centralizing common exception functionality.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'
    default_code = 'server_error'


class NotFoundException(BaseAPIException):
    """
    Exception raised when a requested resource is not found
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'
    default_code = 'not_found'


class BadRequestException(BaseAPIException):
    """
    Exception raised when a request is invalid
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid request.'
    default_code = 'bad_request'


class UnauthorizedException(BaseAPIException):
    """
    Exception raised when a user is not authorized to perform an action
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication credentials were not provided.'
    default_code = 'unauthorized'


class ForbiddenException(BaseAPIException):
    """
    Exception raised when a user is forbidden from performing an action
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'forbidden'


class ServiceException(BaseAPIException):
    """
    Exception raised when a service operation fails
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Service operation failed.'
    default_code = 'service_error'


class ValidationException(BaseAPIException):
    """
    Exception raised when validation fails
    """
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Validation failed.'
    default_code = 'validation_error'
