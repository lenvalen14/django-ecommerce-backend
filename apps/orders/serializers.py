from decimal import Decimal
from django.db import transaction
from rest_framework import serializers

from apps.orders.models import Order, OrderItem, OrderStatus
from apps.products.models import Product


class OrderItemCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product'
    )

    class Meta:
        model = OrderItem
        fields = ('product_id', 'quantity')

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)  # nếu có
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            'product_id',
            'product_name',
            'product_image',
            'quantity',
            'unit_price',
        )

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)  # dùng để tạo
    order_items = OrderItemSerializer(many=True, read_only=True) # dùng để hiển thị sau khi tạo

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = ('id', 'user', 'total_price', 'status', 'created_at', 'items', 'order_items')
        read_only_fields = ('id', 'created_at', 'total_price', 'order_items')


    def create(self, validated_data):
        """
        Tạo đơn hàng kèm các OrderItem liên kết.
        """
        items_data = validated_data.pop('items')

        if not items_data:
            raise serializers.ValidationError({'items': 'Đơn hàng phải có ít nhất một sản phẩm.'})

        with transaction.atomic():
            order = Order.objects.create(user=validated_data['user'], total_price=0)

            final_total_price = Decimal('0.00')

            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']

                # Tạo OrderItem
                unit_price = product.price * quantity
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price
                )

                final_total_price += unit_price

            # Cập nhật lại tổng giá đơn hàng
            order.total_price = final_total_price
            order.save(update_fields=["total_price"])

        return order

class OrderUpdateStatusSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=OrderStatus.choices)

    class Meta:
        model = Order
        fields = ('status',)

    def validate_status(self, value):
        FINAL_STATUSES = {
            OrderStatus.DELIVERED,
            OrderStatus.CANCELED
        }

        if self.instance and self.instance.status in FINAL_STATUSES:
            raise serializers.ValidationError("Đơn hàng đã hoàn tất hoặc hủy thì không được cập nhật.")

        return value
    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save(update_fields=['status'])
        return instance
