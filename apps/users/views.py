import random
import re

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from config import settings
from config.renderers import CustomResponseRenderer
from .models import Address, Profile
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from .serializers import (
    AddressSerializer,
    LoginSerializer,
    ProfileSerializer,
    RegisterSerializer, UserSerializer, ForgetPasswordSerializer, ResetPasswordSerializer, LogoutSerializer,
    VerifyOTPSerializer,
)

User = get_user_model()

@extend_schema(tags=["Auth"])
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    renderer_classes = [CustomResponseRenderer]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "Registered successfully",
            "data": self.get_serializer(user).data
        }, status=status.HTTP_201_CREATED)

@extend_schema(tags=["Auth"])
class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    renderer_classes = [CustomResponseRenderer]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({
            "message": "Logged in successfully",
            "data": serializer.validated_data
        }, status=status.HTTP_200_OK)

@extend_schema(
    tags=["Auth"],
    summary="Đăng xuất",
    description="Thu hồi refresh token và đưa vào blacklist.",
    request=LogoutSerializer,
    responses={205: None, 400: "Bad Request"}
)
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [CustomResponseRenderer]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=["Auth"],
    summary="Gửi mã xác thực",
    description="Gửi mã OTP xác thực qua email (hết hạn sau 5 phút).",
    request={"application/json": {"type": "object", "properties": {
        "email": {"type": "string", "format": "email"}
    }, "required": ["email"]}}
)
class SendOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")

        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return Response({"detail": "Invalid email address"}, status=400)

        otp = random.randint(100000, 999999)
        cache.set(f"otp:{email}", str(otp), timeout=300)  # 5 phút

        try:
            send_mail(
                subject="Mã xác thực OTP của bạn",
                message=f"Mã OTP của bạn là: {otp}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({"detail": f"Failed to send email: {str(e)}"}, status=500)

        return Response({
            "message": "OTP đã được gửi thành công đến email.",
        }, status=status.HTTP_200_OK)

@extend_schema(
    tags=["Auth"],
    summary="Xác thực mã",
)
class VerifyOTPView(APIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "OTP has been verified successfully"}, status=200)

@extend_schema(
    tags=["Auth"],
    summary="Quên mật khẩu (Forget Password)",
    description="Cung cấp email và mật khẩu mới để đặt lại mật khẩu nếu quên. Không yêu cầu xác thực.",
    request=ForgetPasswordSerializer,
    responses={200: ForgetPasswordSerializer}
)
class ForgetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [CustomResponseRenderer]

    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
            "message": "Password has been reset successfully",
            "data": serializer.validated_data
        }, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Auth"],
    summary="Đổi mật khẩu (Reset Password)",
    description="Người dùng đã đăng nhập nhập mật khẩu hiện tại, mật khẩu mới và xác nhận.",
    request=ResetPasswordSerializer,
    responses={200: ResetPasswordSerializer}
)
class ResetPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [CustomResponseRenderer]

    def post(self, request):
        data = request.data.copy()
        data["email"] = request.user.email  # tự động lấy email từ user đã login
        serializer = ResetPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response({
            "message": "Password has been reset successfully",
            "data": serializer.validated_data
        }, status=status.HTTP_200_OK)

@extend_schema(tags=["Users"])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    renderer_classes = [CustomResponseRenderer]

@extend_schema(tags=["Users"])
class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for Profile"""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    pagination_class = PageNumberPagination
    renderer_classes = [CustomResponseRenderer]
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'role', None) == 'admin':
            return self.queryset.all()
        return self.queryset.filter(user=user)

@extend_schema(tags=["Users"])
class AddressViewSet(viewsets.ModelViewSet):
    """ViewSet for Address"""
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    pagination_class = PageNumberPagination
    renderer_classes = [CustomResponseRenderer]
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'role', None) == 'admin':
            return self.queryset.all()
        return self.queryset.filter(user=user)
