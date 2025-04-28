from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserAPITests(APITestCase):
    """
    Test cases for User API endpoints
    """
    def setUp(self):
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            role=User.Role.ADMIN,
            is_staff=True
        )

        self.vendor_user = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='vendorpassword',
            role=User.Role.VENDOR
        )

        self.customer_user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='customerpassword',
            role=User.Role.CUSTOMER
        )

    def authenticate_as_admin(self):
        """Authenticate as admin user"""
        self._authenticate_user(self.admin_user)

    def authenticate_as_vendor(self):
        """Authenticate as vendor user"""
        self._authenticate_user(self.vendor_user)

    def authenticate_as_customer(self):
        """Authenticate as customer user"""
        self._authenticate_user(self.customer_user)

    def _authenticate_user(self, user):
        """Helper method to authenticate a user"""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_register_user(self):
        """Test user registration"""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newuserpassword',
            'password2': 'newuserpassword',
            'first_name': 'New',
            'last_name': 'User',
            'role': User.Role.CUSTOMER
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 4)  # 3 from setup + 1 new
        self.assertEqual(User.objects.get(username='newuser').email, 'newuser@example.com')

    def test_login_user(self):
        """Test user login"""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'customer',
            'password': 'customerpassword'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_list_as_admin(self):
        """Test listing users as admin"""
        url = reverse('user-list')
        self.authenticate_as_admin()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # 3 users from setup

    def test_user_list_as_vendor(self):
        """Test listing users as vendor (should be forbidden)"""
        url = reverse('user-list')
        self.authenticate_as_vendor()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_detail_as_owner(self):
        """Test retrieving user detail as the owner"""
        url = reverse('user-detail', kwargs={'pk': self.customer_user.id})
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'customer')

    def test_user_detail_as_admin(self):
        """Test retrieving user detail as admin"""
        url = reverse('user-detail', kwargs={'pk': self.customer_user.id})
        self.authenticate_as_admin()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'customer')

    def test_user_detail_as_other_user(self):
        """Test retrieving user detail as another user (should be forbidden)"""
        url = reverse('user-detail', kwargs={'pk': self.customer_user.id})
        self.authenticate_as_vendor()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_as_owner(self):
        """Test updating user as the owner"""
        url = reverse('user-detail', kwargs={'pk': self.customer_user.id})
        self.authenticate_as_customer()

        data = {
            'first_name': 'Updated',
            'last_name': 'Customer',
            'email': 'updated.customer@example.com'
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer_user.refresh_from_db()
        self.assertEqual(self.customer_user.first_name, 'Updated')
        self.assertEqual(self.customer_user.email, 'updated.customer@example.com')

    def test_me_endpoint(self):
        """Test the 'me' endpoint for getting current user"""
        url = reverse('user-me')
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'customer')
        self.assertEqual(response.data['email'], 'customer@example.com')


class AuthAPITests(APITestCase):
    def setUp(self):
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin_auth',
            email='admin_auth@example.com',
            password='adminpassword',
            role=User.Role.ADMIN,
            is_staff=True
        )

        self.vendor_user = User.objects.create_user(
            username='vendor_auth',
            email='vendor_auth@example.com',
            password='vendorpassword',
            role=User.Role.VENDOR
        )

        self.customer_user = User.objects.create_user(
            username='customer_auth',
            email='customer_auth@example.com',
            password='customerpassword',
            role=User.Role.CUSTOMER
        )

    def authenticate_as_admin(self):
        """Authenticate as admin user"""
        self._authenticate_user(self.admin_user)

    def authenticate_as_vendor(self):
        """Authenticate as vendor user"""
        self._authenticate_user(self.vendor_user)

    def authenticate_as_customer(self):
        """Authenticate as customer user"""
        self._authenticate_user(self.customer_user)

    def _authenticate_user(self, user):
        """Helper method to authenticate a user"""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_login_valid_credentials(self):
        """Test login with valid credentials"""
        # Create a customer user specifically for this test
        customer = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='customerpassword',
            role=User.Role.CUSTOMER
        )

        url = reverse('token_obtain_pair')
        data = {
            'username': 'customer',
            'password': 'customerpassword'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['username'], 'customer')
        self.assertEqual(response.data['email'], 'customer@example.com')
        self.assertEqual(response.data['role'], User.Role.CUSTOMER)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'customer',
            'password': 'wrongpassword'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test refreshing token"""
        # Create a customer user specifically for this test
        customer = User.objects.create_user(
            username='customer_refresh',
            email='customer_refresh@example.com',
            password='customerpassword',
            role=User.Role.CUSTOMER
        )

        # First login to get refresh token
        login_url = reverse('token_obtain_pair')
        login_data = {
            'username': 'customer_refresh',
            'password': 'customerpassword'
        }

        login_response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        refresh_token = login_response.data['refresh']

        # Then use refresh token to get new access token
        refresh_url = reverse('token_refresh')
        refresh_data = {
            'refresh': refresh_token
        }

        response = self.client.post(refresh_url, refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_logout(self):
        """Test logout endpoint"""
        url = reverse('logout')
        self.authenticate_as_customer()

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully logged out.')
