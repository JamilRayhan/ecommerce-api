# Core App - SOLID Principles Implementation

This core app provides base classes and utilities for implementing SOLID principles in the e-commerce API.

## SOLID Principles

### Single Responsibility Principle (SRP)
- Each class has only one reason to change
- Responsibilities are separated into different classes
- Examples: BaseModel, BaseRepository, BaseService

### Open/Closed Principle (OCP)
- Classes are open for extension but closed for modification
- Base classes provide extension points through inheritance
- Examples: BaseAPIViewSet, BaseModelViewSet

### Liskov Substitution Principle (LSP)
- Derived classes can be substituted for their base classes
- All derived classes maintain the same interface
- Examples: BaseModelViewSet and its subclasses

### Interface Segregation Principle (ISP)
- Clients should not be forced to depend on interfaces they don't use
- Interfaces are specific to client needs
- Examples: IRepository, IService

### Dependency Inversion Principle (DIP)
- High-level modules depend on abstractions, not concrete implementations
- Low-level modules also depend on abstractions
- Examples: Services depend on IRepository, not concrete repositories

## Repository-Service Pattern

The core app implements a repository-service pattern:

1. **Repository Layer**
   - Responsible for data access
   - Abstracts the database operations
   - Implements IRepository interface

2. **Service Layer**
   - Contains business logic
   - Uses repositories for data access
   - Implements IService interface

3. **API Layer**
   - Handles HTTP requests and responses
   - Uses services for business logic
   - Implements BaseAPIViewSet

## Base Classes

### Models
- `BaseModel`: Base model with common fields and methods

### Repositories
- `IRepository`: Interface for repositories
- `BaseRepository`: Base implementation of IRepository

### Services
- `IService`: Interface for services
- `BaseService`: Base implementation of IService

### Serializers
- `BaseModelSerializer`: Base serializer for models
- `BaseCreateUpdateSerializer`: Base serializer for create/update operations
- `BaseReadOnlySerializer`: Base serializer for read-only operations

### Views
- `BaseAPIViewSet`: Base viewset for API endpoints
- `BaseModelViewSet`: Base viewset for CRUD operations
- `BaseReadOnlyViewSet`: Base viewset for read-only operations
- `BaseAPIView`: Base class for API views
- `PublicAPIView`: Base class for public API views (AllowAny)
- `ProtectedAPIView`: Base class for protected API views (IsAuthenticated)

### API Views
- `ListAPIView`: API view for listing objects
- `RetrieveAPIView`: API view for retrieving a single object
- `CreateAPIView`: API view for creating objects
- `UpdateAPIView`: API view for updating objects
- `DestroyAPIView`: API view for deleting objects
- `ListCreateAPIView`: API view for listing and creating objects
- `RetrieveUpdateAPIView`: API view for retrieving and updating objects
- `RetrieveDestroyAPIView`: API view for retrieving and deleting objects
- `RetrieveUpdateDestroyAPIView`: API view for retrieving, updating, and deleting objects
- `PublicListAPIView`: Public API view for listing objects
- `PublicRetrieveAPIView`: Public API view for retrieving a single object
- `PublicListRetrieveAPIView`: Public API view for listing and retrieving objects

### Permissions
- `BasePermission`: Base permission class
- Various role-based permissions

### Utilities
- Caching utilities
- Logging utilities
- Exception handling

## Usage

To use these base classes in your app:

### Repository-Service-ViewSet Pattern

1. Create a repository for your model:
```python
from apps.core.repositories import BaseRepository
from .models import YourModel

class YourModelRepository(BaseRepository):
    def __init__(self):
        super().__init__(YourModel)
```

2. Create a service for your model:
```python
from apps.core.services import BaseService
from .repositories import YourModelRepository

class YourModelService(BaseService):
    def __init__(self):
        super().__init__(YourModelRepository())
```

3. Create a viewset for your model:
```python
from apps.core.views import BaseModelViewSet
from .services import YourModelService
from .serializers import YourModelSerializer

class YourModelViewSet(BaseModelViewSet):
    serializer_class = YourModelSerializer
    service_class = YourModelService
```

### Repository-Service-APIView Pattern

1. Create a repository and service as shown above.

2. Create API views for your model:
```python
from apps.core.api import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .services import YourModelService
from .serializers import YourModelSerializer

class YourModelListCreateView(ListCreateAPIView):
    serializer_class = YourModelSerializer
    service_class = YourModelService

class YourModelDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = YourModelSerializer
    service_class = YourModelService
```

3. Define URLs for your API views:
```python
from django.urls import path
from .views import YourModelListCreateView, YourModelDetailView

urlpatterns = [
    path('your-models/', YourModelListCreateView.as_view(), name='your-model-list'),
    path('your-models/<int:pk>/', YourModelDetailView.as_view(), name='your-model-detail'),
]
```

### Public API Views

For public endpoints that don't require authentication:

```python
from apps.core.api import PublicListRetrieveAPIView
from .services import YourModelService
from .serializers import YourModelSerializer

class PublicYourModelView(PublicListRetrieveAPIView):
    serializer_class = YourModelSerializer
    service_class = YourModelService
```

This structure ensures that your code follows SOLID principles and is maintainable, extensible, and testable.
