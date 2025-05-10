from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic, Type
from django.db.models import Model, QuerySet
from .repositories import IRepository

T = TypeVar('T', bound=Model)


class IService(Generic[T], ABC):
    """
    Interface for service classes.
    Defines the contract that all services must follow.
    
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
    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update an existing entity"""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete an entity"""
        pass
    
    @abstractmethod
    def soft_delete(self, id: int) -> Optional[T]:
        """Soft delete an entity"""
        pass
    
    @abstractmethod
    def filter_by(self, **kwargs) -> QuerySet[T]:
        """Filter entities by given criteria"""
        pass


class BaseService(IService[T]):
    """
    Base implementation of the service interface.
    Provides common business logic methods.
    
    Implements the Dependency Inversion Principle by depending on abstractions.
    """
    
    def __init__(self, repository: IRepository[T]):
        self.repository = repository
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get an entity by its ID"""
        return self.repository.get_by_id(id)
    
    def get_all(self) -> QuerySet[T]:
        """Get all entities"""
        return self.repository.get_all()
    
    def get_active(self) -> QuerySet[T]:
        """Get all active entities"""
        return self.repository.get_active()
    
    def create(self, **kwargs) -> T:
        """Create a new entity"""
        return self.repository.create(**kwargs)
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update an existing entity"""
        instance = self.get_by_id(id)
        if instance:
            return self.repository.update(instance, **kwargs)
        return None
    
    def delete(self, id: int) -> bool:
        """Delete an entity"""
        instance = self.get_by_id(id)
        if instance:
            self.repository.delete(instance)
            return True
        return False
    
    def soft_delete(self, id: int) -> Optional[T]:
        """Soft delete an entity"""
        instance = self.get_by_id(id)
        if instance:
            return self.repository.soft_delete(instance)
        return None
    
    def filter_by(self, **kwargs) -> QuerySet[T]:
        """Filter entities by given criteria"""
        return self.repository.filter_by(**kwargs)
