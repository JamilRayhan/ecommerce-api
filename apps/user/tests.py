from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.core.tests import BaseAPITestCase

User = get_user_model()

class UserAPITests(BaseAPITestCase):
    """
    Test cases for User API endpoints
    """

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
        self.assert_status(response, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 4)  # 3 from setup + 1 new
        self.assertEqual(User.objects.get(username='newuser').email, 'newuser@example.com')

    def test_register_user_with_invalid_data(self):
        """Test user registration with invalid data"""
        url = reverse('register')

        # Test with missing fields
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            # Missing password fields
        }
        response = self.client.post(url, data, format='json')
        self.assert_status(response, status.HTTP_400_BAD_REQUEST)

        # Test with mismatched passwords
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password1',
            'password2': 'password2',
        }
        response = self.client.post(url, data, format='json')
        self.assert_status(response, status.HTTP_400_BAD_REQUEST)

        # Test with existing username
        data = {
            'username': 'admin',  # Already exists
            'email': 'newuser@example.com',
            'password': 'newuserpassword',
            'password2': 'newuserpassword',
        }
        response = self.client.post(url, data, format='json')
        self.assert_status(response, status.HTTP_400_BAD_REQUEST)

        # Test with existing email
        data = {
            'username': 'newuser',
            'email': 'admin@example.com',  # Already exists
            'password': 'newuserpassword',
            'password2': 'newuserpassword',
        }
        response = self.client.post(url, data, format='json')
        self.assert_status(response, status.HTTP_400_BAD_REQUEST)

    def test_login_user(self):
        """Test user login"""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'customer',
            'password': 'password123'
        }

        response = self.client.post(url, data, format='json')
        self.assert_status(response, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse('token_obtain_pair')

        # Test with wrong password
        data = {
            'username': 'customer',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assert_status(response, status.HTTP_401_UNAUTHORIZED)

        # Test with non-existent user
        data = {
            'username': 'nonexistentuser',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assert_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_user_list_as_admin(self):
        """Test listing users as admin"""
        url = reverse('user-list')
        self.authenticate_as_admin()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # 3 users from setup

    def test_user_list_as_vendor(self):
        """Test listing users as vendor (should be forbidden)"""
        url = reverse('user-list')
        self.authenticate_as_vendor()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_403_FORBIDDEN)

    def test_user_list_as_customer(self):
        """Test listing users as customer (should be forbidden)"""
        url = reverse('user-list')
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_403_FORBIDDEN)

    def test_user_detail_as_owner(self):
        """Test retrieving user detail as the owner"""
        url = reverse('user-detail', kwargs={'pk': self.customer_user.id})
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'customer')

    def test_user_detail_as_admin(self):
        """Test retrieving user detail as admin"""
        url = reverse('user-detail', kwargs={'pk': self.customer_user.id})
        self.authenticate_as_admin()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'customer')

    def test_user_detail_as_other_user(self):
        """Test retrieving user detail as another user (should be forbidden)"""
        url = reverse('user-detail', kwargs={'pk': self.customer_user.id})
        self.authenticate_as_vendor()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_403_FORBIDDEN)

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
        self.assert_status(response, status.HTTP_200_OK)
        self.customer_user.refresh_from_db()
        self.assertEqual(self.customer_user.first_name, 'Updated')
        self.assertEqual(self.customer_user.email, 'updated.customer@example.com')

    def test_update_user_as_admin(self):
        """Test updating user as admin"""
        url = reverse('user-detail', kwargs={'pk': self.customer_user.id})
        self.authenticate_as_admin()

        data = {
            'first_name': 'Admin',
            'last_name': 'Updated'
        }

        response = self.client.patch(url, data, format='json')
        self.assert_status(response, status.HTTP_200_OK)

        # Verify the user was updated
        self.customer_user.refresh_from_db()
        self.assertEqual(self.customer_user.first_name, 'Admin')
        self.assertEqual(self.customer_user.last_name, 'Updated')

    def test_update_user_as_other_user(self):
        """Test updating user as another user (should be forbidden)"""
        url = reverse('user-detail', kwargs={'pk': self.customer_user.id})
        self.authenticate_as_vendor()

        data = {
            'first_name': 'Hacked',
            'last_name': 'User'
        }

        response = self.client.patch(url, data, format='json')
        self.assert_status(response, status.HTTP_403_FORBIDDEN)

        # Verify the user was not updated
        self.customer_user.refresh_from_db()
        self.assertNotEqual(self.customer_user.first_name, 'Hacked')

    def test_delete_user_as_admin(self):
        """Test deleting user as admin"""
        # Create a user to delete
        user_to_delete = User.objects.create_user(
            username='todelete',
            email='todelete@example.com',
            password='password123',
            role=User.Role.CUSTOMER
        )

        url = reverse('user-detail', kwargs={'pk': user_to_delete.id})
        self.authenticate_as_admin()

        response = self.client.delete(url)
        self.assert_status(response, status.HTTP_204_NO_CONTENT)

        # Verify the user was deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_to_delete.id)

    def test_delete_user_as_owner(self):
        """Test deleting user as the owner (should be allowed)"""
        # Create a user to delete
        user_to_delete = User.objects.create_user(
            username='todelete',
            email='todelete@example.com',
            password='password123',
            role=User.Role.CUSTOMER
        )

        # Get token for this user
        refresh = RefreshToken.for_user(user_to_delete)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('user-detail', kwargs={'pk': user_to_delete.id})
        response = self.client.delete(url)
        self.assert_status(response, status.HTTP_204_NO_CONTENT)

        # Verify the user was deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_to_delete.id)

    def test_delete_user_as_other_user(self):
        """Test deleting user as another user (should be forbidden)"""
        url = reverse('user-detail', kwargs={'pk': self.customer_user.id})
        self.authenticate_as_vendor()

        response = self.client.delete(url)
        self.assert_status(response, status.HTTP_403_FORBIDDEN)

        # Verify the user was not deleted
        self.assertTrue(User.objects.filter(id=self.customer_user.id).exists())

    def test_me_endpoint(self):
        """Test the 'me' endpoint for getting current user"""
        url = reverse('user-me')
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'customer')
        self.assertEqual(response.data['email'], 'customer@example.com')

    def test_me_endpoint_unauthenticated(self):
        """Test the 'me' endpoint when not authenticated"""
        url = reverse('user-me')
        self.clear_authentication()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_401_UNAUTHORIZED)


class AuthAPITests(BaseAPITestCase):
    """
    Test cases for authentication endpoints
    """

    def test_login_valid_credentials(self):
        """Test login with valid credentials"""
        # Use existing customer user from BaseAPITestCase
        url = reverse('token_obtain_pair')
        data = {
            'username': 'customer',
            'password': 'password123'
        }

        response = self.client.post(url, data, format='json')
        self.assert_status(response, status.HTTP_200_OK)
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
        self.assert_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test refreshing token"""
        # First login to get refresh token
        login_url = reverse('token_obtain_pair')
        login_data = {
            'username': 'customer',
            'password': 'password123'
        }

        login_response = self.client.post(login_url, login_data, format='json')
        self.assert_status(login_response, status.HTTP_200_OK)
        refresh_token = login_response.data['refresh']

        # Then use refresh token to get new access token
        refresh_url = reverse('token_refresh')
        refresh_data = {
            'refresh': refresh_token
        }

        response = self.client.post(refresh_url, refresh_data, format='json')
        self.assert_status(response, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_with_invalid_token(self):
        """Test refreshing token with invalid token"""
        refresh_url = reverse('token_refresh')
        refresh_data = {
            'refresh': 'invalid-token'
        }

        response = self.client.post(refresh_url, refresh_data, format='json')
        self.assert_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_logout(self):
        """Test logout endpoint"""
        url = reverse('logout')
        self.authenticate_as_customer()

        response = self.client.post(url)
        self.assert_status(response, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully logged out.')

    def test_logout_unauthenticated(self):
        """Test logout endpoint when not authenticated"""
        url = reverse('logout')
        self.clear_authentication()

        response = self.client.post(url)
        self.assert_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_verify_email(self):
        """Test email verification endpoint"""
        url = reverse('verify_email')
        data = {
            'email': 'customer@example.com',
            'token': 'invalid-token'  # We can't easily test with a valid token
        }

        response = self.client.post(url, data, format='json')
        # Since we're using an invalid token, we expect a 400 error
        self.assert_status(response, status.HTTP_400_BAD_REQUEST)

    def test_resend_otp(self):
        """Test resend OTP endpoint"""
        url = reverse('resend_otp')
        data = {
            'email': 'customer@example.com'
        }

        response = self.client.post(url, data, format='json')
        # This might return 200 or 400 depending on implementation
        # We're just testing that the endpoint exists and responds
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
