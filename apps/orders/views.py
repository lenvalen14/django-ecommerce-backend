from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample

from apps.orders.models import Order, OrderStatus
from apps.orders.permissions import IsOwner
from apps.orders.serializers import OrderCreateSerializer, OrderUpdateStatusSerializer
from config.renderers import CustomResponseRenderer
from events.handlers.handle_order_canceled import publish_order_canceled_event
from events.handlers.handle_order_created import publish_order_created_event
from events.handlers.handle_order_delivered import publish_order_delivered_event


@extend_schema(tags=["Orders"])
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    pagination_class = PageNumberPagination
    renderer_classes = [CustomResponseRenderer]

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'cancel', 'update_status', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'role', None) == 'admin':
            return self.queryset.all()
        return self.queryset.filter(user=user)

    @extend_schema(
        summary="Tạo đơn hàng mới",
        description="Tạo một đơn hàng mới kèm danh sách sản phẩm. Đồng thời trừ kho.",
        responses={201: OrderCreateSerializer},
        examples=[
            OpenApiExample(
                name="Tạo đơn hàng mẫu",
                value={
                    "items": [
                        {"product_id": 1, "quantity": 2},
                        {"product_id": 5, "quantity": 1}
                    ]
                },
                request_only=True,
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        publish_order_created_event(order)
        return Response({
            "message": "Created order successfully",
            "data": OrderCreateSerializer(order).data
        }, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Danh sách đơn hàng",
        responses={200: OrderCreateSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "message": "List of orders get successfully",
                "data": serializer.data
            })

        # fallback nếu không paginate
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "message": "List of orders get successfully",
            "data": serializer.data
        })

    @extend_schema(
        summary="Cập nhật trạng thái đơn hàng",
        description="Chỉ cho phép cập nhật trạng thái từ các trạng thái đang xử lý sang trạng thái tiếp theo hợp lệ.",
        request=OrderUpdateStatusSerializer,
    )
    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        order = self.get_object()
        user = request.user

        status_value = request.data.get('status')
        if not status_value:
            return Response({'message': 'Trường status là bắt buộc.'}, status=400)

        is_admin = user.is_staff or getattr(user, 'role', None) == 'admin'

        # Các trạng thái mà user được phép cập nhật
        allowed_user_statuses = [OrderStatus.CANCELED, OrderStatus.RETURNED]

        if not is_admin and status_value not in allowed_user_statuses:
            return Response({'message': "You don't have permission to change the order status"}, status=403)

        if order.status != 'DELIVERED' and status_value == 'delivered':
            publish_order_delivered_event(order)

        serializer = OrderUpdateStatusSerializer(order, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'message': 'Update status successfully',
            'data': OrderUpdateStatusSerializer(order).data
        }, status=200)

    @action(detail=True, methods=['post'], url_path='cancel')
    @extend_schema(
        summary="Huỷ đơn hàng",
        description="Huỷ đơn hàng khi đang ở trạng thái PENDING.",
        request=None,
    )
    def cancel(self, request, pk=None):
        with transaction.atomic():
            order = self.get_object()
            order.refresh_from_db()

            if order.status != OrderStatus.PENDING:
                return Response({
                    'message': "Can't cancel order",
                }, status=400)

            publish_order_canceled_event(order)

            order.status = OrderStatus.CANCELED
            order.save(update_fields=['status'])

            return Response({
                'message': 'Cancel order successfully.',
                'data': OrderUpdateStatusSerializer(order).data
            }, status=200)

