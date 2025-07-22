from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, ProfileViewSet, AddressViewSet, UserViewSet, ForgetPasswordView, \
    ResetPasswordView, LogoutView, SendOTPView, VerifyOTPView

router = DefaultRouter()
router.register('profiles', ProfileViewSet, basename='profiles')
router.register('addresses', AddressViewSet, basename='addresses')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('sendOTP/', SendOTPView.as_view(), name='send_otp'),
    path('verifyOTP/', VerifyOTPView.as_view(), name='verify_otp'),
    path("forgot-password/", ForgetPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path('', include(router.urls)),
]