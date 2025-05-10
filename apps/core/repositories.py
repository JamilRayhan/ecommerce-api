from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic, Type
from django.db.models import Model, QuerySet

T = TypeVar('T', bound=Model)


class IRepository(Generic[T], ABC):
    """
    Interface for repository classes.
    Defines the contract that all repositories must follow.
    
    Implements the Interface Segregation Principle by defining a clear contract.
    """
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Get an entity by its ID"""
        pass
    
    @abstractmethod
    def get_all(self) -> QuerySet[T]:
        """Get all entities"""
        pass
    
    @abstractmethod
    def get_active(self) -> QuerySet[T]:
        """Get all active entities"""
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> T:
        """Create a new entity"""
        pass
    
    @abstractmethod
    def update(self, instance: T, **kwargs) -> T:
        """Update an existing entity"""
        pass
    
    @abstractmethod
    def delete(self, instance: T) -> None:
        """Delete an entity"""
        pass
    
    @abstractmethod
    def soft_delete(self, instance: T) -> T:
        """Soft delete an entity"""
        pass
    
    @abstractmethod
    def filter_by(self, **kwargs) -> QuerySet[T]:
        """Filter entities by given criteria"""
        pass


class BaseRepository(IRepository[T]):
    """
    Base implementation of the repository interface.
    Provides common data access methods.
    
    Implements the Dependency Inversion Principle by depending on abstractions.
    """
    
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get an entity by its ID"""
        try:
            return self.model_class.objects.get(id=id)
        except self.model_class.DoesNotExist:
            return None
    
    def get_all(self) -> QuerySet[T]:
        """Get all entities"""
        return self.model_class.objects.all()
    
    def get_active(self) -> QuerySet[T]:
        """Get all active entities"""
        return self.model_class.objects.filter(is_active=True)
    
    def create(self, **kwargs) -> T:
        """Create a new entity"""
        return self.model_class.objects.create(**kwargs)
    
    def update(self, instance: T, **kwargs) -> T:
        """Update an existing entity"""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    def delete(self, instance: T) -> None:
        """Delete an entity"""
        instance.delete()
    
    def soft_delete(self, instance: T) -> T:
        """Soft delete an entity"""
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])
        return instance
    
    def filter_by(self, **kwargs) -> QuerySet[T]:
        """Filter entities by given criteria"""
        return self.model_class.objects.filter(**kwargs)
