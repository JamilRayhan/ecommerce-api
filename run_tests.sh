#!/bin/bash

# Run all tests
python manage.py test apps.user.tests apps.vendor.tests apps.product.tests apps.order.tests apps.notification.tests --verbosity=2

# Run with coverage report (uncomment to use)
# python -m coverage run --source='apps' manage.py test apps.user.tests apps.vendor.tests apps.product.tests apps.order.tests apps.notification.tests
# python -m coverage report
# python -m coverage html  # Creates htmlcov/index.html

# Run specific app tests (uncomment and modify as needed)
# python manage.py test apps.user.tests
# python manage.py test apps.vendor.tests
# python manage.py test apps.product.tests
# python manage.py test apps.order.tests
# python manage.py test apps.notification.tests
