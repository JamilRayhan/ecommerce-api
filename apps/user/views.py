from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserProfileSerializer, EmailVerificationSerializer, ResendOTPSerializer
from .permissions import IsAdmin, IsOwnerOrAdmin
from .utils import send_otp_email

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users
    """
    queryset = User.objects.all().order_by('id')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserSerializer
        return UserProfileSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrAdmin]
        elif self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        elif self.action == 'me':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Get the current user's profile
        """
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # Set role based on request data or default to customer
        role = self.request.data.get('role', User.Role.CUSTOMER)
        serializer.save(role=role)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def verify_email(self, request):
        """
        Verify email with OTP
        """
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)

            # User is now verified and active
            user.is_active = True
            user.save()

            return Response({
                'message': 'Email verified successfully. You can now log in.',
                'email': email
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def resend_otp(self, request):
        """
        Resend OTP for email verification
        """
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)

            # Generate new OTP and send verification email
            otp = user.generate_email_verification_token()
            send_otp_email(user, otp)

            return Response({
                'message': 'OTP sent successfully to your email.',
                'email': email
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
