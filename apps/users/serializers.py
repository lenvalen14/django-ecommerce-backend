from django.core.cache import cache
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import Profile, Address
from django.contrib.auth.models import update_last_login

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer cho model User.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role')


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer cho model Profile.
    """
    avatar = serializers.ImageField(required=False)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ('id', 'user', 'phone', 'avatar', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Profile.objects.create(**validated_data)


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer cho model Address.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Address
        fields = (
            'id', 'user', 'addressLine', 'city', 'phone',
            'is_default', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Address.objects.create(**validated_data)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']  #mật khẩu sẽ được băm
        )

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        print(email, password)

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Email or password is incorrect")

        refresh = RefreshToken.for_user(user)
        update_last_login(None, user)
        return {
            "accessToken": str(refresh.access_token),
            "refreshToken": str(refresh),
            "user": UserSerializer(user).data
        }

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = attrs.get("refresh")
        if not refresh:
            raise serializers.ValidationError("Missing refresh token")
        return attrs

class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("User not found")

        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords don't match")

        user.set_password(new_password)
        user.save()

        return {"message": "Password has been reset"}

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("User not found")
        if not user.check_password(password):
            raise serializers.ValidationError("Password doesn't match")
        if new_password != confirm_password:
            raise serializers.ValidationError("New password doesn't match")
        user.set_password(new_password)
        user.save()
        return {"message": "Password has been reset"}

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get("email")
        otp = attrs.get("otp")

        # Kiểm tra người dùng tồn tại
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("User not found")

        # Lấy OTP trong cache
        cached_otp = cache.get(f"otp:{email}")
        if not cached_otp:
            raise serializers.ValidationError("OTP expired or not found")

        if otp != cached_otp:
            raise serializers.ValidationError("Invalid OTP")

        return attrs

    def save(self, **kwargs):
        email = self.validated_data["email"]
        cache.delete(f"otp:{email}")
        return {"message": "OTP verified successfully"}

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate(self, attrs):
        email = attrs.get("email")
        if not email:
            raise serializers.ValidationError("Email is required")


