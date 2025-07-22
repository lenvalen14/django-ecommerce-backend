"""
Models for user account, profile, and address management.
"""

from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Người dùng kế thừa từ AbstractUser, bổ sung trường role để phân quyền.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer'
    )

    def is_admin(self) -> bool:
        """
        Kiểm tra người dùng có phải là admin không.
        """
        return self.role == 'admin'


class Profile(models.Model):
    # pylint: disable=too-few-public-methods
    """
    Hồ sơ mở rộng cho người dùng: avatar và số điện thoại.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=11, unique=True)
    avatar = CloudinaryField('avatar')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta-options for the Profile model."""
        ordering = ['-created_at']

    def __str__(self) -> str:
        # pylint: disable=no-member
        return str(self.user.username)


class Address(models.Model):
    # pylint: disable=too-few-public-methods
    """
    Địa chỉ người dùng: địa chỉ cụ thể, thành phố, số điện thoại liên hệ.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    addressLine = models.TextField()
    city = models.CharField(max_length=20)
    phone = models.CharField(max_length=11)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for the Address model."""
        ordering = ['-created_at']
        verbose_name_plural = 'Addresses'

    def __str__(self) -> str:
        return f"{self.user.username} live at {self.city} has number phone is: {self.phone}"