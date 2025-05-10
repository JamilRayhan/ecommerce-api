from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserProfileSerializer, EmailVerificationSerializer, ResendOTPSerializer
from .permissions import IsAdmin, IsOwnerOrAdmin
from .services import UserService
from apps.core.views import BaseModelViewSet

User = get_user_model()

class UserViewSet(BaseModelViewSet):
    """
    API endpoint for users
    """
    serializer_class = UserProfileSerializer
    service_class = UserService
    serializer_classes = {
        'create': UserSerializer,
        'update': UserSerializer,
        'partial_update': UserSerializer,
    }

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrAdmin]
        elif self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        elif self.action == 'me':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['verify_email', 'resend_otp']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Get the current user's profile
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # Set role based on request data or default to customer
        role = self.request.data.get('role', User.Role.CUSTOMER)

        # Use the service to register the user
        service = self.get_service()
        validated_data = serializer.validated_data
        validated_data['role'] = role

        # Remove password2 if it exists
        if 'password2' in validated_data:
            validated_data.pop('password2')

        instance = service.register_user(**validated_data)
        serializer.instance = instance

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def verify_email(self, request):
        """
        Verify email with OTP
        """
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            token = serializer.validated_data['token']

            # Get the user by email
            service = self.get_service()
            user = service.get_by_email(email)

            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Verify the email
            if service.verify_email(user.id, token):
                return Response({
                    'message': 'Email verified successfully. You can now log in.',
                    'email': email
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def resend_otp(self, request):
        """
        Resend OTP for email verification
        """
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            # Get the user by email
            service = self.get_service()
            user = service.get_by_email(email)

            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Resend verification email
            if service.resend_verification_email(user.id):
                return Response({
                    'message': 'OTP sent successfully to your email.',
                    'email': email
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to send OTP'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
