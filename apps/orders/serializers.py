from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.orders.models import Order, OrderItem
from apps.products.models import Product


class OrderItemCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product'
    )

    class Meta:
        model = OrderItem
        fields = ('product_id', 'quantity')


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)  # dùng để tạo
    order_items = OrderItemCreateSerializer(many=True, read_only=True)  # dùng để hiển thị sau khi tạo

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = ('id', 'user', 'total_price', 'created_at', 'items', 'order_items')
        read_only_fields = ('id', 'created_at', 'total_price', 'order_items')


    def create(self, validated_data):
        """
        Tạo đơn hàng kèm các OrderItem liên kết.
        Đồng thời trừ kho từng sản phẩm.
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

                # Trừ tồn kho
                try:
                    product.decrease_stock(quantity)
                except ValidationError as e:
                    raise serializers.ValidationError({'detail': str(e)})

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
