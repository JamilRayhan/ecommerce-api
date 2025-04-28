# E-commerce API

A multi-tenant e-commerce API with role-based access control built with Django and Django REST Framework. This API provides a comprehensive backend solution for e-commerce platforms with separate roles for administrators, vendors, and customers.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## Features

- **User Management**
  - Role-based access control (Admin, Vendor, Customer)
  - JWT authentication with token refresh
  - User registration and profile management
  - Secure password handling

- **Vendor Management**
  - Vendor profiles with company information
  - Vendor-specific product management
  - Order tracking for vendor products

- **Product Management**
  - Product categories
  - Product creation, updating, and deletion
  - Product search and filtering
  - Featured products

- **Order Processing**
  - Shopping cart functionality
  - Order creation and management
  - Order status tracking
  - Order history

- **Notification System**
  - Real-time notifications for users
  - Order placement notifications for customers
  - Product order notifications for vendors
  - Order status update notifications
  - Notification read/unread status tracking

- **Security**
  - Permission-based access control
  - JWT token authentication
  - Environment-based configuration
  - Email verification with OTP
  - SMTP email integration

- **Notifications & Caching**
  - Real-time notifications for users
  - Django signals for order notifications
  - Redis caching for improved performance
  - Email notifications for verification

- **Logging & Monitoring**
  - Comprehensive logging system
  - Daily log rotation with 30-day retention
  - Separate error logs
  - Email notifications for critical errors

## Technology Stack

- **Backend Framework**: Django 5.1.5
- **API Framework**: Django REST Framework 3.14.0
- **Authentication**: JWT (djangorestframework-simplejwt 5.5.0)
- **Database**: SQLite (default), PostgreSQL (configurable)
- **Documentation**: Swagger/OpenAPI (drf-yasg)
- **Environment Management**: python-dotenv
- **Caching**: Django Redis
- **Utilities**: Django Model Utils for field tracking

## Project Structure

The project follows a modular structure with separate Django apps for different functionalities:

```
ecommerce_api/
├── apps/
│   ├── user/            # User authentication and management
│   │   ├── models.py    # Custom User model with role-based access
│   │   ├── views.py     # User API endpoints
│   │   ├── serializers.py # User data serialization
│   │   ├── permissions.py # Custom permission classes
│   │   └── tests.py     # User API tests
│   │
│   ├── vendor/          # Vendor profiles and management
│   │   ├── models.py    # Vendor model
│   │   ├── views.py     # Vendor API endpoints
│   │   ├── serializers.py # Vendor data serialization
│   │   └── tests.py     # Vendor API tests
│   │
│   ├── product/         # Product catalog and categories
│   │   ├── models.py    # Product and Category models
│   │   ├── views.py     # Product API endpoints
│   │   ├── serializers.py # Product data serialization
│   │   └── tests.py     # Product API tests
│   │
│   ├── order/           # Order processing and history
│   │   ├── models.py    # Order and OrderItem models
│   │   ├── views.py     # Order API endpoints
│   │   ├── serializers.py # Order data serialization
│   │   ├── signals.py   # Order-related signals for notifications
│   │   └── tests.py     # Order API tests
│   │
│   ├── notification/    # User notifications system
│   │   ├── models.py    # Notification model
│   │   ├── views.py     # Notification API endpoints
│   │   ├── serializers.py # Notification data serialization
│   │   ├── signals.py   # Notification signals
│   │   └── tests.py     # Notification API tests
│   │
├── ecommerce_api/       # Project settings and configuration
│   ├── settings.py      # Django settings including caching
│   ├── urls.py          # Main URL routing
│   └── wsgi.py          # WSGI configuration
│
├── .env                 # Environment variables (create from .env.example)
├── .env.example         # Example environment variables
├── manage.py            # Django management script
├── requirements.txt     # Project dependencies
├── run_tests.sh         # Test runner script
├── LICENSE              # MIT License
└── README.md            # Project documentation
```

## Setup and Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecommerce_api
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

## Environment Variables

The following environment variables can be configured in the `.env` file:

```
SECRET_KEY=your-secret-key-here
DEBUG=True/False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings
# SQLite (default)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# PostgreSQL example
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=your_db_name
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=localhost
# DB_PORT=5432

# Redis cache (optional)
# REDIS_URL=redis://localhost:6379/1
```

## Running the Application

Start the development server:

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`.

## API Endpoints

### Authentication

- `POST /api/v1/auth/register/`: Register a new user
- `POST /api/v1/auth/verify-email/`: Verify email with OTP
- `POST /api/v1/auth/resend-otp/`: Resend OTP for email verification
- `POST /api/v1/auth/login/`: Login and get JWT tokens
- `POST /api/v1/auth/refresh/`: Refresh JWT token
- `POST /api/v1/auth/logout/`: Logout (client-side)

### Users

- `GET /api/v1/users/`: List all users (admin only)
- `GET /api/v1/users/{id}/`: Get user details
- `PATCH /api/v1/users/{id}/`: Update user
- `DELETE /api/v1/users/{id}/`: Delete user
- `GET /api/v1/users/me/`: Get current user profile

### Vendors

- `GET /api/v1/vendors/`: List all vendors
- `POST /api/v1/vendors/`: Create a vendor profile
- `GET /api/v1/vendors/{id}/`: Get vendor details
- `PATCH /api/v1/vendors/{id}/`: Update vendor (owner or admin)
- `DELETE /api/v1/vendors/{id}/`: Delete vendor (owner or admin)
- `GET /api/v1/vendors/me/`: Get current vendor profile

### Products

- `GET /api/v1/products/`: List all products
- `POST /api/v1/products/`: Create a product (vendor only)
- `GET /api/v1/products/{id}/`: Get product details
- `PATCH /api/v1/products/{id}/`: Update product (owner or admin)
- `DELETE /api/v1/products/{id}/`: Delete product (owner or admin)
- `GET /api/v1/products/featured/`: Get featured products

### Categories

- `GET /api/v1/categories/`: List all categories
- `POST /api/v1/categories/`: Create a category (admin only)
- `GET /api/v1/categories/{id}/`: Get category details
- `PATCH /api/v1/categories/{id}/`: Update category (admin only)
- `DELETE /api/v1/categories/{id}/`: Delete category (admin only)

### Orders

- `GET /api/v1/orders/`: List orders (filtered by user role)
- `POST /api/v1/orders/`: Create a new order
- `GET /api/v1/orders/{id}/`: Get order details
- `POST /api/v1/orders/{id}/update_status/`: Update order status (admin only)
- `GET /api/v1/orders/vendor_orders/`: Get orders for current vendor

### Notifications

- `GET /api/v1/notifications/`: List all notifications for current user
- `GET /api/v1/notifications/{id}/`: Get notification details
- `GET /api/v1/notifications/unread/`: Get unread notifications
- `POST /api/v1/notifications/{id}/mark_as_read/`: Mark notification as read
- `POST /api/v1/notifications/mark_all_as_read/`: Mark all notifications as read

The notification system automatically creates notifications for:
- Customers when they place an order
- Vendors when their products are ordered
- Customers when their order status changes

## Authentication

The API uses JWT (JSON Web Tokens) for authentication with email verification:

1. **Registration and Email Verification**:
   - Register a user with email and password
   - A 6-digit OTP is sent to the user's email
   - User must verify their email by submitting the OTP
   - Once verified, the user can log in

2. **Login and Token Usage**:
   - Login to get access and refresh tokens
   - Include the access token in the Authorization header of your requests:
     ```
     Authorization: Bearer <your-access-token>
     ```
   - When the access token expires, use the refresh token to get a new access token

3. **Email Verification Endpoints**:
   - `/api/v1/auth/verify-email/`: Verify email with OTP
   - `/api/v1/auth/resend-otp/`: Resend OTP if needed

## Notification System

The notification system provides real-time notifications for users based on various events in the system. It uses Django signals to automatically create notifications when certain actions occur, such as order placement or status updates.

### Features

- **User-specific notifications**: Each user sees only their own notifications
- **Notification types**: Different types of notifications (order placed, order updated, etc.)
- **Read/unread status**: Track which notifications have been read
- **Caching**: Optimized performance with Redis caching
- **API endpoints**: Comprehensive API for managing notifications

### Implementation

The notification system is implemented in the `apps/notification` app and consists of:

1. **Notification Model**: Stores notification data including recipient, type, message, and read status
2. **Django Signals**: Automatically creates notifications when orders are placed or updated
3. **API Endpoints**: Allows users to view and manage their notifications
4. **Caching**: Uses Redis (when available) to cache notifications for improved performance

### How Notifications Work

1. **Order Placement**:
   - When a customer places an order, a signal is triggered in `apps/order/signals.py`
   - The signal creates a notification for the customer confirming their order
   - For each product in the order, a notification is created for the vendor

2. **Order Status Updates**:
   - When an order's status is updated, a signal is triggered in `apps/notification/signals.py`
   - The signal creates a notification for the customer informing them of the status change

3. **Notification Delivery**:
   - Notifications are stored in the database and can be retrieved via the API
   - The API supports filtering to show only unread notifications
   - Notifications can be marked as read individually or all at once

### Example Notification Flow

1. Customer places an order for products from Vendor A and Vendor B
2. Customer receives a notification: "Order #ABC123 Placed"
3. Vendor A receives a notification: "New Order #ABC123"
4. Vendor B receives a notification: "New Order #ABC123"
5. Admin updates order status to "Shipped"
6. Customer receives a notification: "Order #ABC123 Updated to Shipped"

## Logging

The project includes a comprehensive logging system that captures various levels of information:

### Log Configuration

- **General Logs**: All application activities are logged to `logs/ecommerce_api.log`
- **Error Logs**: Errors are separately logged to `logs/error.log`
- **Log Rotation**: Logs are rotated daily and kept for 30 days
- **Admin Notifications**: Critical errors are emailed to administrators

### Log Levels

- **DEBUG**: Detailed information, typically useful only for diagnosing problems
- **INFO**: Confirmation that things are working as expected
- **WARNING**: Indication that something unexpected happened, but the application still works
- **ERROR**: Due to a more serious problem, the application has not been able to perform a function
- **CRITICAL**: A serious error, indicating that the application itself may be unable to continue running

### Using Logs in Code

```python
import logging

# Get a logger for your module
logger = logging.getLogger('apps.your_app_name')

# Log messages at different levels
logger.debug('Detailed debug information')
logger.info('Something noteworthy happened')
logger.warning('Something unexpected happened')
logger.error('A more serious problem occurred')
logger.critical('A critical error occurred')
```

## Testing

The project includes comprehensive tests for all API endpoints. You can run the tests using the provided script:

```bash
bash run_tests.sh
```

Or directly with Django:

```bash
python manage.py test apps.user.tests apps.vendor.tests apps.product.tests apps.order.tests apps.notification.tests
```

To run tests for a specific app:

```bash
python manage.py test apps.user.tests
```

## API Documentation

API documentation is automatically generated and available at:

- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

These provide interactive documentation of all API endpoints, request/response formats, and authentication requirements.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
