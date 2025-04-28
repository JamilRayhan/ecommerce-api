from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import random
import string
from datetime import datetime, timedelta

class User(AbstractUser):
    """
    Custom User model with role-based access control
    """
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        VENDOR = 'VENDOR', _('Vendor')
        CUSTOMER = 'CUSTOMER', _('Customer')

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )

    email = models.EmailField(unique=True)

    # Add additional fields as needed
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Email verification fields
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_token_created_at = models.DateTimeField(blank=True, null=True)

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_vendor(self):
        return self.role == self.Role.VENDOR

    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    def generate_email_verification_token(self):
        """Generate a 6-digit OTP for email verification"""
        otp = ''.join(random.choices(string.digits, k=6))
        self.email_verification_token = otp
        self.email_verification_token_created_at = timezone.now()
        self.save(update_fields=['email_verification_token', 'email_verification_token_created_at'])
        return otp

    def verify_email(self, token):
        """Verify the email with the provided token"""
        # Check if token is valid
        if not self.email_verification_token or self.email_verification_token != token:
            return False

        # Check if token is expired (10 minutes)
        if not self.email_verification_token_created_at:
            return False

        expiration_time = self.email_verification_token_created_at + timedelta(minutes=10)
        if timezone.now() > expiration_time:
            return False

        # Mark email as verified
        self.is_email_verified = True
        self.email_verification_token = None
        self.email_verification_token_created_at = None
        self.save(update_fields=['is_email_verified', 'email_verification_token', 'email_verification_token_created_at'])
        return True
