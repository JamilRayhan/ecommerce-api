from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .views import PublicAPIView, ProtectedAPIView


class ListAPIView(ProtectedAPIView):
    """
    API view for listing objects.
    Handles GET requests to list all objects.
    """
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET request to list objects
        """
        return self.list(request, *args, **kwargs)


class RetrieveAPIView(ProtectedAPIView):
    """
    API view for retrieving a single object.
    Handles GET requests to retrieve an object by ID.
    """
    
    def get(self, request, pk, *args, **kwargs):
        """
        Handle GET request to retrieve an object
        """
        return self.retrieve(request, pk, *args, **kwargs)


class CreateAPIView(ProtectedAPIView):
    """
    API view for creating objects.
    Handles POST requests to create a new object.
    """
    
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to create an object
        """
        return self.create(request, *args, **kwargs)


class UpdateAPIView(ProtectedAPIView):
    """
    API view for updating objects.
    Handles PUT and PATCH requests to update an object.
    """
    
    def put(self, request, pk, *args, **kwargs):
        """
        Handle PUT request to update an object
        """
        return self.update(request, pk, *args, **kwargs)
    
    def patch(self, request, pk, *args, **kwargs):
        """
        Handle PATCH request to partially update an object
        """
        return self.partial_update(request, pk, *args, **kwargs)


class DestroyAPIView(ProtectedAPIView):
    """
    API view for deleting objects.
    Handles DELETE requests to delete an object.
    """
    
    def delete(self, request, pk, *args, **kwargs):
        """
        Handle DELETE request to delete an object
        """
        return self.destroy(request, pk, *args, **kwargs)


class ListCreateAPIView(ListAPIView, CreateAPIView):
    """
    API view for listing and creating objects.
    Handles GET and POST requests.
    """
    pass


class RetrieveUpdateAPIView(RetrieveAPIView, UpdateAPIView):
    """
    API view for retrieving and updating objects.
    Handles GET, PUT, and PATCH requests.
    """
    pass


class RetrieveDestroyAPIView(RetrieveAPIView, DestroyAPIView):
    """
    API view for retrieving and deleting objects.
    Handles GET and DELETE requests.
    """
    pass


class RetrieveUpdateDestroyAPIView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    API view for retrieving, updating, and deleting objects.
    Handles GET, PUT, PATCH, and DELETE requests.
    """
    pass


class PublicListAPIView(PublicAPIView):
    """
    Public API view for listing objects.
    Handles GET requests to list all objects.
    """
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET request to list objects
        """
        return self.list(request, *args, **kwargs)


class PublicRetrieveAPIView(PublicAPIView):
    """
    Public API view for retrieving a single object.
    Handles GET requests to retrieve an object by ID.
    """
    
    def get(self, request, pk, *args, **kwargs):
        """
        Handle GET request to retrieve an object
        """
        return self.retrieve(request, pk, *args, **kwargs)


class PublicListRetrieveAPIView(PublicListAPIView, PublicRetrieveAPIView):
    """
    Public API view for listing and retrieving objects.
    Handles GET requests for both list and detail views.
    """
    pass
