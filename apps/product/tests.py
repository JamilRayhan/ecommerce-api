from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Product, Category
from apps.vendor.models import Vendor

User = get_user_model()

class CategoryAPITests(APITestCase):
    """
    Test cases for Category API endpoints
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

        # Create category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Category Description'
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

    def test_category_list(self):
        """Test listing categories"""
        url = reverse('category-list')
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # 1 category from setup

    def test_category_detail(self):
        """Test retrieving category detail"""
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Category')

    def test_create_category_as_admin(self):
        """Test creating a category as admin"""
        url = reverse('category-list')
        self.authenticate_as_admin()

        data = {
            'name': 'New Category',
            'description': 'New Category Description'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the category was created
        self.assertEqual(Category.objects.count(), 2)  # 1 from setup + 1 new
        self.assertEqual(Category.objects.get(name='New Category').description, 'New Category Description')

    def test_create_category_as_non_admin(self):
        """Test creating a category as non-admin (should be forbidden)"""
        url = reverse('category-list')
        self.authenticate_as_vendor()

        data = {
            'name': 'New Category',
            'description': 'New Category Description'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify the category was not created
        self.assertEqual(Category.objects.count(), 1)

    def test_update_category_as_admin(self):
        """Test updating a category as admin"""
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        self.authenticate_as_admin()

        data = {
            'name': 'Updated Category',
            'description': 'Updated Category Description'
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the category was updated
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category')
        self.assertEqual(self.category.description, 'Updated Category Description')

    def test_update_category_as_non_admin(self):
        """Test updating a category as non-admin (should be forbidden)"""
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        self.authenticate_as_vendor()

        data = {
            'name': 'Hacked Category',
            'description': 'Hacked Category Description'
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify the category was not updated
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Test Category')


class ProductAPITests(APITestCase):
    def setUp(self):
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin_product',
            email='admin_product@example.com',
            password='adminpassword',
            role=User.Role.ADMIN,
            is_staff=True
        )

        self.vendor_user = User.objects.create_user(
            username='vendor_product',
            email='vendor_product@example.com',
            password='vendorpassword',
            role=User.Role.VENDOR
        )

        self.customer_user = User.objects.create_user(
            username='customer_product',
            email='customer_product@example.com',
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

        # Create category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Category Description'
        )

        # Create product
        self.product = Product.objects.create(
            vendor=self.vendor,
            category=self.category,
            name='Test Product',
            description='Test Product Description',
            price=99.99,
            stock=10,
            is_available=True
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

    def test_product_list(self):
        """Test listing products"""
        url = reverse('product-list')
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # 1 product from setup

    def test_product_detail(self):
        """Test retrieving product detail"""
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')
        self.assertEqual(response.data['vendor']['company_name'], 'Test Vendor')

    def test_create_product_as_vendor(self):
        """Test creating a product as vendor"""
        url = reverse('product-list')
        self.authenticate_as_vendor()

        data = {
            'category_id': self.category.id,
            'name': 'New Product',
            'description': 'New Product Description',
            'price': 49.99,
            'stock': 20,
            'is_available': True
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the product was created
        self.assertEqual(Product.objects.count(), 2)  # 1 from setup + 1 new
        new_product = Product.objects.get(name='New Product')
        self.assertEqual(float(new_product.price), 49.99)
        self.assertEqual(new_product.vendor, self.vendor)

    def test_create_product_as_customer(self):
        """Test creating a product as customer (should be forbidden)"""
        url = reverse('product-list')
        self.authenticate_as_customer()

        data = {
            'category_id': self.category.id,
            'name': 'New Product',
            'description': 'New Product Description',
            'price': 49.99,
            'stock': 20,
            'is_available': True
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify the product was not created
        self.assertEqual(Product.objects.count(), 1)

    def test_update_product_as_vendor_owner(self):
        """Test updating a product as the vendor owner"""
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        self.authenticate_as_vendor()

        data = {
            'name': 'Updated Product',
            'description': 'Updated Product Description',
            'price': 79.99
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the product was updated
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product')
        self.assertEqual(float(self.product.price), 79.99)

    def test_update_product_as_non_owner(self):
        """Test updating a product as non-owner (should be forbidden)"""
        # Create a new vendor and authenticate as them
        new_vendor_user = self.customer_user  # Use the customer user for this test
        new_vendor_user.role = new_vendor_user.Role.VENDOR
        new_vendor_user.save()

        url = reverse('product-detail', kwargs={'pk': self.product.id})
        self.authenticate_as_customer()

        data = {
            'name': 'Hacked Product',
            'description': 'Hacked Product Description',
            'price': 0.01
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify the product was not updated
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Test Product')

    def test_delete_product_as_vendor_owner(self):
        """Test deleting a product as the vendor owner"""
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        self.authenticate_as_vendor()

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify the product was deleted
        self.assertEqual(Product.objects.count(), 0)

    def test_delete_product_as_non_owner(self):
        """Test deleting a product as non-owner (should be forbidden)"""
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        self.authenticate_as_customer()

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify the product was not deleted
        self.assertEqual(Product.objects.count(), 1)

    def test_featured_products(self):
        """Test the featured products endpoint"""
        url = reverse('product-featured')
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # 1 product from setup
