from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.user.models import User
from apps.vendor.models import Vendor
from apps.product.models import Category, Product
from apps.order.models import Order, OrderItem
from .models import Notification
from apps.core.tests import BaseAPITestCase
from decimal import Decimal

class NotificationAPITests(BaseAPITestCase):
    """
    Test cases for the Notification API
    """
    def setUp(self):
        super().setUp()

        # Create vendor profile for the vendor user
        self.vendor = Vendor.objects.create(
            user=self.vendor_user,
            company_name='Test Vendor',
            description='Test vendor description',
            address='123 Vendor St'
        )

        # Create category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )

        # Create product
        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description',
            price=Decimal('99.99'),
            vendor=self.vendor,
            category=self.category,
            stock=100,
            is_available=True
        )

        # Create notifications
        self.notification_customer = Notification.objects.create(
            recipient=self.customer_user,
            notification_type=Notification.NotificationType.SYSTEM,
            title='Test Notification for Customer',
            message='This is a test notification for the customer'
        )

        self.notification_vendor = Notification.objects.create(
            recipient=self.vendor_user,
            notification_type=Notification.NotificationType.SYSTEM,
            title='Test Notification for Vendor',
            message='This is a test notification for the vendor'
        )

    def test_list_notifications_as_customer(self):
        """Test listing notifications as customer"""
        self.authenticate_as_customer()
        url = reverse('notification-list')

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Notification for Customer')

    def test_list_notifications_as_vendor(self):
        """Test listing notifications as vendor"""
        self.authenticate_as_vendor()
        url = reverse('notification-list')

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Notification for Vendor')

    def test_list_notifications_unauthenticated(self):
        """Test listing notifications when not authenticated"""
        self.clear_authentication()
        url = reverse('notification-list')

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_notification_detail_as_owner(self):
        """Test retrieving notification detail as the owner"""
        self.authenticate_as_customer()
        url = reverse('notification-detail', kwargs={'pk': self.notification_customer.id})

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Notification for Customer')

    def test_notification_detail_not_found(self):
        """Test retrieving non-existent notification detail"""
        self.authenticate_as_customer()
        url = reverse('notification-detail', kwargs={'pk': 999})

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_404_NOT_FOUND)

    def test_notification_detail_as_non_owner(self):
        """Test retrieving notification detail as non-owner (should be forbidden)"""
        self.authenticate_as_vendor()
        url = reverse('notification-detail', kwargs={'pk': self.notification_customer.id})

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_404_NOT_FOUND)

    def test_mark_notification_as_read(self):
        """Test marking a notification as read"""
        self.authenticate_as_customer()
        url = reverse('notification-mark-as-read', kwargs={'pk': self.notification_customer.id})

        response = self.client.post(url)
        self.assert_status(response, status.HTTP_200_OK)

        # Verify notification is marked as read
        self.notification_customer.refresh_from_db()
        self.assertTrue(self.notification_customer.is_read)

    def test_mark_notification_as_read_non_owner(self):
        """Test marking a notification as read as non-owner"""
        self.authenticate_as_vendor()
        url = reverse('notification-mark-as-read', kwargs={'pk': self.notification_customer.id})

        response = self.client.post(url)
        self.assert_status(response, status.HTTP_404_NOT_FOUND)

        # Verify notification is still unread
        self.notification_customer.refresh_from_db()
        self.assertFalse(self.notification_customer.is_read)

    def test_mark_all_notifications_as_read(self):
        """Test marking all notifications as read"""
        # Create another notification for the customer
        Notification.objects.create(
            recipient=self.customer_user,
            notification_type=Notification.NotificationType.SYSTEM,
            title='Another Test Notification',
            message='This is another test notification'
        )

        self.authenticate_as_customer()
        url = reverse('notification-mark-all-as-read')

        response = self.client.post(url)
        self.assert_status(response, status.HTTP_200_OK)

        # Verify all notifications are marked as read
        unread_count = Notification.objects.filter(
            recipient=self.customer_user,
            is_read=False
        ).count()
        self.assertEqual(unread_count, 0)

    def test_unread_notifications(self):
        """Test getting unread notifications"""
        # Create a read notification
        Notification.objects.create(
            recipient=self.customer_user,
            notification_type=Notification.NotificationType.SYSTEM,
            title='Read Notification',
            message='This notification is already read',
            is_read=True
        )

        self.authenticate_as_customer()
        url = reverse('notification-unread')

        response = self.client.get(url)
        self.assert_status(response, status.HTTP_200_OK)

        # Should only return unread notifications
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Notification for Customer')

    def test_order_notification_creation(self):
        """Test that notifications are created when an order is placed"""
        self.authenticate_as_customer()

        # Create an order
        order_data = {
            'shipping_address': '123 Test St, Test City',
            'items': [
                {
                    'product_id': self.product.id,
                    'quantity': 2
                }
            ]
        }

        url = reverse('order-list')
        response = self.client.post(url, order_data, format='json')
        self.assert_status(response, status.HTTP_201_CREATED)

        # Get the order from the database
        order = Order.objects.filter(customer=self.customer_user).latest('created_at')
        order_id = order.id

        # Verify customer notification was created
        customer_notifications = Notification.objects.filter(
            recipient=self.customer_user,
            notification_type=Notification.NotificationType.ORDER_PLACED,
            related_object_id=order_id
        )
        self.assertTrue(customer_notifications.exists())

        # Verify vendor notification was created
        vendor_notifications = Notification.objects.filter(
            recipient=self.vendor_user,
            notification_type=Notification.NotificationType.ORDER_PLACED,
            related_object_id=order_id
        )
        self.assertTrue(vendor_notifications.exists())
