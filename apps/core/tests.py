from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from typing import Dict, Any, List, Optional
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class BaseTestCase(TestCase):
    """
    Base test case for all tests
    """
    
    def setUp(self):
        """
        Set up test data
        """
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True
        )
        
        self.vendor_user = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='password123',
            role=User.Role.VENDOR
        )
        
        self.customer_user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='password123',
            role=User.Role.CUSTOMER
        )


class BaseAPITestCase(APITestCase):
    """
    Base API test case for all API tests
    """
    
    def setUp(self):
        """
        Set up test data
        """
        self.client = APIClient()
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True
        )
        
        self.vendor_user = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='password123',
            role=User.Role.VENDOR
        )
        
        self.customer_user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='password123',
            role=User.Role.CUSTOMER
        )
    
    def authenticate_as_admin(self):
        """
        Authenticate as admin user
        """
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    
    def authenticate_as_vendor(self):
        """
        Authenticate as vendor user
        """
        token = RefreshToken.for_user(self.vendor_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    
    def authenticate_as_customer(self):
        """
        Authenticate as customer user
        """
        token = RefreshToken.for_user(self.customer_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    
    def clear_authentication(self):
        """
        Clear authentication credentials
        """
        self.client.credentials()
    
    def assert_status(self, response, expected_status):
        """
        Assert that the response has the expected status code
        """
        self.assertEqual(response.status_code, expected_status)
    
    def assert_response_keys(self, response, expected_keys):
        """
        Assert that the response contains the expected keys
        """
        for key in expected_keys:
            self.assertIn(key, response.data)
