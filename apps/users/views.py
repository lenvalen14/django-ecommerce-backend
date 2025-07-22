from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from config.renderers import CustomResponseRenderer
from .models import Address, Profile
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from .serializers import (
    AddressSerializer,
    LoginSerializer,
    ProfileSerializer,
    RegisterSerializer, UserSerializer,
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
