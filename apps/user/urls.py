from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from .auth import CustomTokenObtainPairView, TokenRefreshView, RegisterView, LogoutView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/verify-email/', UserViewSet.as_view({'post': 'verify_email'}), name='verify_email'),
    path('auth/resend-otp/', UserViewSet.as_view({'post': 'resend_otp'}), name='resend_otp'),
]
