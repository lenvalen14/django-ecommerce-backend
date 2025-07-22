"""
Serializers cho ứng dụng products.

Định nghĩa cách dữ liệu Product và Category được chuyển đổi thành JSON.
"""
from rest_framework import serializers

from apps.products.models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer cho model Category.
    Chỉ hiển thị những thông tin cần thiết của danh mục.
    """
    class Meta:
        """Meta-options cho CategorySerializer."""
        model = Category
        fields = ('id', 'category_name')


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer cho model Product.
    - Khi đọc (GET): Hiển thị chi tiết category (dạng nested object).
    - Khi ghi (POST/PUT): Chấp nhận 'category_id' để tạo hoặc cập nhật quan hệ.
    """
    image = serializers.ImageField(required=False)
    category = CategorySerializer(read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        """Meta options cho ProductSerializer."""
        model = Product
        fields = (
            'id',
            'product_name',
            'description',
            'image',
            'price',
            'stock_quantity',
            'category',
            'category_id'
        )