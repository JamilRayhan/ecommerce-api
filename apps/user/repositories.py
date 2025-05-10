from django.contrib.auth import get_user_model
from apps.core.repositories import BaseRepository
from typing import Optional, List, Dict, Any, Union
from django.db.models import Q, QuerySet

User = get_user_model()


class UserRepository(BaseRepository):
    """
    Repository for User model
    """
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username
        """
        try:
            return self.model_class.objects.get(username=username)
        except self.model_class.DoesNotExist:
            return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email
        """
        try:
            return self.model_class.objects.get(email=email)
        except self.model_class.DoesNotExist:
            return None
    
    def get_by_role(self, role: str) -> QuerySet:
        """
        Get users by role
        """
        return self.model_class.objects.filter(role=role)
    
    def get_admins(self) -> QuerySet:
        """
        Get all admin users
        """
        return self.get_by_role(User.Role.ADMIN)
    
    def get_vendors(self) -> QuerySet:
        """
        Get all vendor users
        """
        return self.get_by_role(User.Role.VENDOR)
    
    def get_customers(self) -> QuerySet:
        """
        Get all customer users
        """
        return self.get_by_role(User.Role.CUSTOMER)
    
    def search(self, query: str) -> QuerySet:
        """
        Search users by username, email, first_name, or last_name
        """
        return self.model_class.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    
    def create_user(self, **kwargs) -> User:
        """
        Create a new user
        """
        return self.model_class.objects.create_user(**kwargs)
    
    def create_superuser(self, **kwargs) -> User:
        """
        Create a new superuser
        """
        return self.model_class.objects.create_superuser(**kwargs)
    
    def update_password(self, user_id: int, password: str) -> Optional[User]:
        """
        Update a user's password
        """
        user = self.get_by_id(user_id)
        if user:
            user.set_password(password)
            user.save()
            return user
        return None
    
    def verify_email(self, user_id: int, token: str) -> bool:
        """
        Verify a user's email
        """
        user = self.get_by_id(user_id)
        if user:
            return user.verify_email(token)
        return False
    
    def generate_email_verification_token(self, user_id: int) -> Optional[str]:
        """
        Generate an email verification token for a user
        """
        user = self.get_by_id(user_id)
        if user:
            return user.generate_email_verification_token()
        return None
