from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, ProfileViewSet, AddressViewSet, UserViewSet

router = DefaultRouter()
router.register('profiles', ProfileViewSet, basename='profiles')
router.register('addresses', AddressViewSet, basename='addresses')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
]