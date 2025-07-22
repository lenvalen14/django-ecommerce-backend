from rest_framework import viewsets, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample

from apps.orders.models import Order
from apps.orders.serializers import OrderCreateSerializer
from config.renderers import CustomResponseRenderer


@extend_schema(tags=["Orders"])
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    pagination_class = PageNumberPagination
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [CustomResponseRenderer]

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
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "message": "List of orders",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
