from rest_framework import viewsets, mixins, status, views
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from typing import Type, Dict, Any, Optional, List, Callable
from django.db.models import Model, QuerySet
from django.http import Http404
from .services import IService
from .serializers import BaseModelSerializer


class BaseAPIViewSet(viewsets.GenericViewSet):
    """
    Base API viewset that all viewsets should inherit from.
    Provides common API functionality.

    Implements the Open/Closed Principle by allowing extension without modification.
    """

    service_class = None
    serializer_class = None
    serializer_classes = {}

    def get_service(self) -> IService:
        """
        Get the service instance
        """
        if not self.service_class:
            raise NotImplementedError("Service class must be defined")
        return self.service_class()

    def get_serializer_class(self):
        """
        Return the serializer class based on the current action
        """
        return self.serializer_classes.get(self.action, self.serializer_class)

    def get_queryset(self) -> QuerySet:
        """
        Get the queryset for the viewset
        """
        service = self.get_service()
        queryset = service.get_all()

        # Apply eager loading if available
        serializer_class = self.get_serializer_class()
        if hasattr(serializer_class, 'setup_eager_loading'):
            queryset = serializer_class.setup_eager_loading(queryset)

        return queryset


class BaseModelViewSet(BaseAPIViewSet,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin):
    """
    Base model viewset that provides CRUD operations.

    Implements the Liskov Substitution Principle by ensuring all derived viewsets
    can be used interchangeably.
    """

    def perform_create(self, serializer):
        """
        Create a new instance using the service
        """
        service = self.get_service()
        validated_data = serializer.validated_data
        instance = service.create(**validated_data)
        serializer.instance = instance

    def perform_update(self, serializer):
        """
        Update an instance using the service
        """
        service = self.get_service()
        instance = self.get_object()
        validated_data = serializer.validated_data
        updated_instance = service.update(instance.id, **validated_data)
        serializer.instance = updated_instance

    def perform_destroy(self, instance):
        """
        Delete an instance using the service
        """
        service = self.get_service()
        service.delete(instance.id)

    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        """
        Soft delete an instance
        """
        service = self.get_service()
        instance = service.soft_delete(pk)
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        Restore a soft-deleted instance
        """
        service = self.get_service()
        instance = service.get_by_id(pk)
        if instance:
            instance.restore()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)


class BaseReadOnlyViewSet(BaseAPIViewSet,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin):
    """
    Base read-only viewset that provides retrieve and list operations.
    """
    pass


class BaseAPIView(views.APIView):
    """
    Base API view that all API views should inherit from.
    Provides common API functionality.

    Implements the Open/Closed Principle by allowing extension without modification.
    """

    service_class = None
    serializer_class = None

    def get_service(self) -> IService:
        """
        Get the service instance
        """
        if not self.service_class:
            raise NotImplementedError("Service class must be defined")
        return self.service_class()

    def get_object(self, pk):
        """
        Get an object by its primary key
        """
        service = self.get_service()
        instance = service.get_by_id(pk)
        if not instance:
            raise Http404("Object not found")
        return instance

    def get_serializer(self, *args, **kwargs):
        """
        Get a serializer instance
        """
        serializer_class = self.serializer_class
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_serializer_context(self):
        """
        Get the serializer context
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def list(self, request, *args, **kwargs):
        """
        List all objects
        """
        service = self.get_service()
        queryset = service.get_active()

        # Apply filters if available
        filter_kwargs = {}
        for key, value in request.query_params.items():
            if key not in ['page', 'page_size', 'format']:
                filter_kwargs[key] = value

        if filter_kwargs:
            queryset = service.filter_by(**filter_kwargs)

        # Serialize the data
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk, *args, **kwargs):
        """
        Retrieve a single object
        """
        instance = self.get_object(pk)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create a new object
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create the object using the service
        service = self.get_service()
        instance = service.create(**serializer.validated_data)

        # Return the created object
        result_serializer = self.get_serializer(instance)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk, *args, **kwargs):
        """
        Update an existing object
        """
        instance = self.get_object(pk)
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)

        # Update the object using the service
        service = self.get_service()
        updated_instance = service.update(pk, **serializer.validated_data)

        # Return the updated object
        result_serializer = self.get_serializer(updated_instance)
        return Response(result_serializer.data)

    def partial_update(self, request, pk, *args, **kwargs):
        """
        Partially update an existing object
        """
        kwargs['partial'] = True
        return self.update(request, pk, *args, **kwargs)

    def destroy(self, request, pk, *args, **kwargs):
        """
        Delete an object
        """
        instance = self.get_object(pk)
        service = self.get_service()
        service.delete(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def soft_delete(self, request, pk, *args, **kwargs):
        """
        Soft delete an object
        """
        instance = self.get_object(pk)
        service = self.get_service()
        updated_instance = service.soft_delete(pk)
        serializer = self.get_serializer(updated_instance)
        return Response(serializer.data)


class PublicAPIView(BaseAPIView):
    """
    Base API view for public endpoints.
    Allows any user to access the view.
    """

    permission_classes = [AllowAny]


class ProtectedAPIView(BaseAPIView):
    """
    Base API view for protected endpoints.
    Requires authentication to access the view.
    """

    permission_classes = [IsAuthenticated]
