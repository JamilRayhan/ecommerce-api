from apps.core.services import BaseService
from .repositories import UserRepository
from django.contrib.auth import get_user_model
from typing import Optional, List, Dict, Any, Union
from django.db.models import QuerySet
from .utils import send_otp_email

User = get_user_model()


class UserService(BaseService):
    """
    Service for User model
    """
    
    def __init__(self):
        super().__init__(UserRepository())
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username
        """
        return self.repository.get_by_username(username)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email
        """
        return self.repository.get_by_email(email)
    
    def get_by_role(self, role: str) -> QuerySet:
        """
        Get users by role
        """
        return self.repository.get_by_role(role)
    
    def get_admins(self) -> QuerySet:
        """
        Get all admin users
        """
        return self.repository.get_admins()
    
    def get_vendors(self) -> QuerySet:
        """
        Get all vendor users
        """
        return self.repository.get_vendors()
    
    def get_customers(self) -> QuerySet:
        """
        Get all customer users
        """
        return self.repository.get_customers()
    
    def search(self, query: str) -> QuerySet:
        """
        Search users by username, email, first_name, or last_name
        """
        return self.repository.search(query)
    
    def register_user(self, **kwargs) -> User:
        """
        Register a new user
        """
        # Create the user
        user = self.repository.create_user(**kwargs)
        
        # Generate OTP and send verification email
        otp = self.repository.generate_email_verification_token(user.id)
        send_otp_email(user, otp)
        
        return user
    
    def create_superuser(self, **kwargs) -> User:
        """
        Create a new superuser
        """
        return self.repository.create_superuser(**kwargs)
    
    def update_password(self, user_id: int, password: str) -> Optional[User]:
        """
        Update a user's password
        """
        return self.repository.update_password(user_id, password)
    
    def verify_email(self, user_id: int, token: str) -> bool:
        """
        Verify a user's email
        """
        return self.repository.verify_email(user_id, token)
    
    def resend_verification_email(self, user_id: int) -> bool:
        """
        Resend verification email
        """
        user = self.get_by_id(user_id)
        if user and not user.is_email_verified:
            otp = self.repository.generate_email_verification_token(user_id)
            send_otp_email(user, otp)
            return True
        return False
    
    def update_profile(self, user_id: int, **kwargs) -> Optional[User]:
        """
        Update a user's profile
        """
        return self.update(user_id, **kwargs)
    
    def change_role(self, user_id: int, role: str) -> Optional[User]:
        """
        Change a user's role
        """
        if role not in [choice[0] for choice in User.Role.choices]:
            return None
        return self.update(user_id, role=role)
