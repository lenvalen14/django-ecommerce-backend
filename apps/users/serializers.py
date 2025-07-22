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
