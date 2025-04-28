from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .utils import send_otp_email

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'password2', 'role', 'phone_number', 'address')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        # Only validate passwords if they are provided
        if 'password' in attrs and 'password2' in attrs:
            if attrs['password'] != attrs['password2']:
                raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        # Remove password2 if it exists
        if 'password2' in validated_data:
            validated_data.pop('password2')

        # Set is_active to False until email is verified
        validated_data['is_active'] = False

        # Create the user
        user = User.objects.create_user(**validated_data)

        # Generate OTP and send verification email
        otp = user.generate_email_verification_token()
        send_otp_email(user, otp)

        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            # Remove password2 if it exists
            if 'password2' in validated_data:
                validated_data.pop('password2')
            instance.set_password(password)

        return super().update(instance, validated_data)

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile (without password fields)
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'address', 'is_email_verified')
        read_only_fields = ('role', 'is_email_verified')

class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification with OTP
    """
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, min_length=6, max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User with this email does not exist."})

        if user.is_email_verified:
            raise serializers.ValidationError({"email": "Email is already verified."})

        if not user.verify_email(otp):
            raise serializers.ValidationError({"otp": "Invalid or expired OTP."})

        return attrs

class ResendOTPSerializer(serializers.Serializer):
    """
    Serializer for resending OTP
    """
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User with this email does not exist."})

        if user.is_email_verified:
            raise serializers.ValidationError({"email": "Email is already verified."})

        return attrs
