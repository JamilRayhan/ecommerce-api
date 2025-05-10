# Run all tests
python manage.py test apps.user.tests apps.vendor.tests apps.product.tests apps.order.tests apps.notification.tests --keepdb --parallel --failfast

# Run specific app tests (uncomment and modify as needed)
# python manage.py test apps.user.tests
# python manage.py test apps.vendor.tests
# python manage.py test apps.product.tests
# python manage.py test apps.order.tests
# python manage.py test apps.notification.tests
