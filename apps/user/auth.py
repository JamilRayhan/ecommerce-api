from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status, permissions, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer to include user role and other info
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role

        return token

    def validate(self, attrs):
        # Check if user exists
        user = User.objects.filter(username=attrs['username']).first()

        # Check if email is verified
        if user and not user.is_email_verified:
            raise exceptions.AuthenticationFailed(
                'Email not verified. Please check your email for verification instructions.',
                code='email_not_verified'
            )

        data = super().validate(attrs)

        # Add extra responses
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['role'] = self.user.role
        data['is_email_verified'] = self.user.is_email_verified

        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token view using our custom serializer
    """
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(APIView):
    """
    API endpoint for user registration
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Registration successful. Please check your email for verification instructions.',
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'is_email_verified': user.is_email_verified
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """
    API endpoint for user logout (client-side only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # JWT is stateless, so logout is handled client-side
        # by removing the token
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
