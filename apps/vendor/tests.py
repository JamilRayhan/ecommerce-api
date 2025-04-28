from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Vendor

User = get_user_model()

class VendorAPITests(APITestCase):
    """
    Test cases for Vendor API endpoints
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

        # Create vendor profile
        self.vendor = Vendor.objects.create(
            user=self.vendor_user,
            company_name='Test Vendor',
            description='Test Vendor Description',
            address='123 Vendor St'
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

    def test_vendor_list(self):
        """Test listing vendors"""
        url = reverse('vendor-list')
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # 1 vendor from setup

    def test_vendor_detail(self):
        """Test retrieving vendor detail"""
        url = reverse('vendor-detail', kwargs={'pk': self.vendor.id})
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'Test Vendor')
        self.assertEqual(response.data['user']['username'], 'vendor')

    def test_create_vendor_as_non_vendor_user(self):
        """Test creating a vendor profile as a non-vendor user"""
        url = reverse('vendor-list')
        self.authenticate_as_customer()

        data = {
            'company_name': 'New Vendor',
            'description': 'New Vendor Description',
            'address': '456 New Vendor St'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the customer user's role was updated to vendor
        self.customer_user.refresh_from_db()
        self.assertEqual(self.customer_user.role, self.customer_user.Role.VENDOR)

        # Verify the vendor was created
        self.assertEqual(Vendor.objects.count(), 2)  # 1 from setup + 1 new
        new_vendor = Vendor.objects.get(company_name='New Vendor')
        self.assertEqual(new_vendor.user, self.customer_user)

    def test_update_vendor_as_owner(self):
        """Test updating vendor as the owner"""
        url = reverse('vendor-detail', kwargs={'pk': self.vendor.id})
        self.authenticate_as_vendor()

        data = {
            'company_name': 'Updated Vendor',
            'description': 'Updated Vendor Description'
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the vendor was updated
        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.company_name, 'Updated Vendor')
        self.assertEqual(self.vendor.description, 'Updated Vendor Description')

    def test_update_vendor_as_non_owner(self):
        """Test updating vendor as non-owner (should be forbidden)"""
        url = reverse('vendor-detail', kwargs={'pk': self.vendor.id})
        self.authenticate_as_customer()

        data = {
            'company_name': 'Hacked Vendor',
            'description': 'Hacked Vendor Description'
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify the vendor was not updated
        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.company_name, 'Test Vendor')

    def test_update_vendor_as_admin(self):
        """Test updating vendor as admin"""
        url = reverse('vendor-detail', kwargs={'pk': self.vendor.id})
        self.authenticate_as_admin()

        data = {
            'company_name': 'Admin Updated Vendor',
            'description': 'Admin Updated Vendor Description'
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the vendor was updated
        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.company_name, 'Admin Updated Vendor')

    def test_delete_vendor_as_owner(self):
        """Test deleting vendor as the owner"""
        url = reverse('vendor-detail', kwargs={'pk': self.vendor.id})
        self.authenticate_as_vendor()

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify the vendor was deleted
        self.assertEqual(Vendor.objects.count(), 0)

    def test_delete_vendor_as_non_owner(self):
        """Test deleting vendor as non-owner (should be forbidden)"""
        url = reverse('vendor-detail', kwargs={'pk': self.vendor.id})
        self.authenticate_as_customer()

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify the vendor was not deleted
        self.assertEqual(Vendor.objects.count(), 1)

    def test_vendor_me_endpoint(self):
        """Test the 'me' endpoint for getting current vendor"""
        url = reverse('vendor-me')
        self.authenticate_as_vendor()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'Test Vendor')
        self.assertEqual(response.data['user']['username'], 'vendor')
