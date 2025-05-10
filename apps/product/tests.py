from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Product, Category
from apps.vendor.models import Vendor
from apps.core.tests import BaseAPITestCase

User = get_user_model()

class CategoryAPITests(BaseAPITestCase):
    """
    Test cases for Category API endpoints
    """
    def setUp(self):
        super().setUp()

        # Create vendor profile for the vendor user
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

    def test_category_list(self):
        """Test listing categories"""
        url = reverse('category-list')
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # 1 category from setup

    def test_category_detail(self):
        """Test retrieving category detail"""
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Category')

    def test_category_detail_not_found(self):
        """Test retrieving non-existent category detail"""
        url = reverse('category-detail', kwargs={'pk': 999})
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_404_NOT_FOUND)

    def test_create_category_as_admin(self):
        """Test creating a category as admin"""
        url = reverse('category-list')
        self.authenticate_as_admin()

        data = {
            'name': 'New Category',
            'description': 'New Category Description'
        }

        response = self.client.post(url, data, format='json')
        self.assert_status(response, status.HTTP_201_CREATED)

        # Verify the category was created
        self.assertEqual(Category.objects.count(), 2)  # 1 from setup + 1 new
        self.assertEqual(Category.objects.get(name='New Category').description, 'New Category Description')

    def test_create_category_with_invalid_data(self):
        """Test creating a category with invalid data"""
        url = reverse('category-list')
        self.authenticate_as_admin()

        # Empty name (should be invalid)
        data = {
            'name': '',
            'description': 'New Category Description'
        }

        response = self.client.post(url, data, format='json')
        self.assert_status(response, status.HTTP_400_BAD_REQUEST)

        # Verify no category was created
        self.assertEqual(Category.objects.count(), 1)  # Still only 1 from setup

    def test_create_category_as_non_admin(self):
        """Test creating a category as non-admin (should be forbidden)"""
        url = reverse('category-list')
        self.authenticate_as_vendor()

        data = {
            'name': 'New Category',
            'description': 'New Category Description'
        }

        response = self.client.post(url, data, format='json')
        self.assert_status(response, status.HTTP_403_FORBIDDEN)

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
        self.assert_status(response, status.HTTP_200_OK)

        # Verify the category was updated
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category')
        self.assertEqual(self.category.description, 'Updated Category Description')

    def test_update_category_with_invalid_data(self):
        """Test updating a category with invalid data"""
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        self.authenticate_as_admin()

        # Empty name (should be invalid)
        data = {
            'name': '',
        }

        response = self.client.patch(url, data, format='json')
        self.assert_status(response, status.HTTP_400_BAD_REQUEST)

        # Verify the category was not updated
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Test Category')

    def test_update_category_as_non_admin(self):
        """Test updating a category as non-admin (should be forbidden)"""
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        self.authenticate_as_vendor()

        data = {
            'name': 'Hacked Category',
            'description': 'Hacked Category Description'
        }

        response = self.client.patch(url, data, format='json')
        self.assert_status(response, status.HTTP_403_FORBIDDEN)

        # Verify the category was not updated
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Test Category')

    def test_delete_category_as_admin(self):
        """Test deleting a category as admin"""
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        self.authenticate_as_admin()

        response = self.client.delete(url)
        self.assert_status(response, status.HTTP_204_NO_CONTENT)

        # Verify the category was deleted
        self.assertEqual(Category.objects.count(), 0)

    def test_delete_category_as_non_admin(self):
        """Test deleting a category as non-admin (should be forbidden)"""
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        self.authenticate_as_vendor()

        response = self.client.delete(url)
        self.assert_status(response, status.HTTP_403_FORBIDDEN)

        # Verify the category was not deleted
        self.assertEqual(Category.objects.count(), 1)


class ProductAPITests(BaseAPITestCase):
    """
    Test cases for Product API endpoints
    """
    def setUp(self):
        super().setUp()

        # Create vendor profile for the vendor user
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

    def test_product_list(self):
        """Test listing products"""
        url = reverse('product-list')
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # 1 product from setup

    def test_product_detail(self):
        """Test retrieving product detail"""
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')
        self.assertEqual(response.data['vendor']['company_name'], 'Test Vendor')

    def test_product_detail_not_found(self):
        """Test retrieving non-existent product detail"""
        url = reverse('product-detail', kwargs={'pk': 999})
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_404_NOT_FOUND)

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
        self.assert_status(response, status.HTTP_201_CREATED)

        # Verify the product was created
        self.assertEqual(Product.objects.count(), 2)  # 1 from setup + 1 new
        new_product = Product.objects.get(name='New Product')
        self.assertEqual(float(new_product.price), 49.99)
        self.assertEqual(new_product.vendor, self.vendor)

    def test_create_product_with_invalid_data(self):
        """Test creating a product with invalid data"""
        url = reverse('product-list')
        self.authenticate_as_vendor()

        # Missing required fields
        data = {
            'name': 'New Product',
            # Missing category_id, description, price
        }

        response = self.client.post(url, data, format='json')
        self.assert_status(response, status.HTTP_400_BAD_REQUEST)

        # Verify no product was created
        self.assertEqual(Product.objects.count(), 1)  # Still only 1 from setup

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
        self.assert_status(response, status.HTTP_403_FORBIDDEN)

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
        self.assert_status(response, status.HTTP_200_OK)

        # Verify the product was updated
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product')
        self.assertEqual(float(self.product.price), 79.99)

    def test_update_product_with_invalid_data(self):
        """Test updating a product with invalid data"""
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        self.authenticate_as_vendor()

        # Invalid price (negative)
        data = {
            'price': -10.00,
        }

        response = self.client.patch(url, data, format='json')
        self.assert_status(response, status.HTTP_400_BAD_REQUEST)

        # Verify the product was not updated
        self.product.refresh_from_db()
        self.assertEqual(float(self.product.price), 99.99)

    def test_update_product_as_non_owner(self):
        """Test updating a product as non-owner (should be forbidden)"""
        # Create a new vendor and authenticate as them
        new_vendor_user = User.objects.create_user(
            username='another_vendor',
            email='another_vendor@example.com',
            password='password123',
            role=User.Role.VENDOR
        )

        # Create vendor profile for the new vendor user
        Vendor.objects.create(
            user=new_vendor_user,
            company_name='Another Vendor',
            description='Another Vendor Description',
            address='456 Vendor St'
        )

        # Authenticate as the new vendor
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(new_vendor_user).access_token}')

        url = reverse('product-detail', kwargs={'pk': self.product.id})

        data = {
            'name': 'Hacked Product',
            'description': 'Hacked Product Description',
            'price': 0.01
        }

        response = self.client.patch(url, data, format='json')
        self.assert_status(response, status.HTTP_403_FORBIDDEN)

        # Verify the product was not updated
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Test Product')

    def test_delete_product_as_vendor_owner(self):
        """Test deleting a product as the vendor owner"""
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        self.authenticate_as_vendor()

        response = self.client.delete(url)
        self.assert_status(response, status.HTTP_204_NO_CONTENT)

        # Verify the product was deleted
        self.assertEqual(Product.objects.count(), 0)

    def test_delete_product_as_non_owner(self):
        """Test deleting a product as non-owner (should be forbidden)"""
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        self.authenticate_as_customer()

        response = self.client.delete(url)
        self.assert_status(response, status.HTTP_403_FORBIDDEN)

        # Verify the product was not deleted
        self.assertEqual(Product.objects.count(), 1)

    def test_delete_product_as_admin(self):
        """Test deleting a product as admin"""
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        self.authenticate_as_admin()

        response = self.client.delete(url)
        self.assert_status(response, status.HTTP_204_NO_CONTENT)

        # Verify the product was deleted
        self.assertEqual(Product.objects.count(), 0)

    def test_featured_products(self):
        """Test the featured products endpoint"""
        url = reverse('product-featured')
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # 1 product from setup

    def test_featured_products_unauthenticated(self):
        """Test the featured products endpoint when not authenticated"""
        url = reverse('product-featured')
        self.clear_authentication()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_filter_products_by_category(self):
        """Test filtering products by category"""
        # Create another category and product
        another_category = Category.objects.create(
            name='Another Category',
            description='Another Category Description'
        )

        # Create product in the new category (this will be excluded from the filter)
        Product.objects.create(
            vendor=self.vendor,
            category=another_category,
            name='Another Product',
            description='Another Product Description',
            price=149.99,
            stock=5,
            is_available=True
        )

        # Filter by the original category
        url = f"{reverse('product-list')}?category={self.category.id}"
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Product')

    def test_filter_products_by_price_range(self):
        """Test filtering products by price range"""
        # Create another product with higher price (this will be included in the filter)
        Product.objects.create(
            vendor=self.vendor,
            category=self.category,
            name='Expensive Product',
            description='Expensive Product Description',
            price=999.99,
            stock=1,
            is_available=True
        )

        # Filter by price range
        url = f"{reverse('product-list')}?min_price=100&max_price=1000"
        self.authenticate_as_customer()

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Expensive Product')
