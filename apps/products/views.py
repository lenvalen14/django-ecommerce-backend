from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from apps.products.models import Product, Category
from apps.products.permissions import IsAdminOrReadOnly
from config.renderers import CustomResponseRenderer
from apps.products.serializers import ProductSerializer, CategorySerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter


@extend_schema(tags=["Products"])
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    renderer_classes = [CustomResponseRenderer]
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(
        summary= "Danh sách các danh mục",
        description= "Lấy danh sách toàn bộ danh mục, có phân trang",
        responses={200: CategorySerializer(many=True)},
        parameters=[OpenApiParameter(name="page", type=int, location=OpenApiParameter.QUERY)]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Chi tiết danh mục",
        description="Lấy thông tin chi tiết của một danh mục",
        responses={200: CategorySerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Tạo danh mục",
        description="Tạo thông tin của một danh mục",
        responses={200: CategorySerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Cập nhật toàn bộ thông tin danh mục",
        description="PUT toàn bộ thông tin danh mục",
        request=CategorySerializer,
        responses={200: CategorySerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Cập nhật một phần danh mục",
        description="PATCH một vài trường thông tin danh mục",
        request=CategorySerializer,
        responses={200: CategorySerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Xóa danh mục",
        description="Xóa một danh mục khỏi hệ thống",
        responses={204: OpenApiResponse(description="Deleted successfully")}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

@extend_schema(tags=["Products"])
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination
    renderer_classes = [CustomResponseRenderer]
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        category_pk = self.kwargs.get('category_pk')
        if category_pk:
            category = get_object_or_404(Category, pk=category_pk)
            return Product.objects.filter(category=category)
        return super().get_queryset()

    @extend_schema(
        summary="Danh sách sản phẩm",
        description="Lấy danh sách toàn bộ sản phẩm, có phân trang",
        responses={200: ProductSerializer(many=True)},
        parameters=[
            OpenApiParameter(name="page", type=int, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="category", type=int, location=OpenApiParameter.QUERY, required=False, description="Lọc theo category id")
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Chi tiết sản phẩm",
        description="Lấy thông tin chi tiết của một sản phẩm",
        responses={200: ProductSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Tạo sản phẩm mới",
        description="API tạo mới sản phẩm có upload hình ảnh",
        responses={201: ProductSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response({
            'message': 'Product created successfully',
            'code': status.HTTP_201_CREATED,
            'data': self.get_serializer(product).data
        }, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Cập nhật toàn bộ sản phẩm",
        description="PUT toàn bộ thông tin sản phẩm",
        request=ProductSerializer,
        responses={200: ProductSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Cập nhật một phần sản phẩm",
        description="PATCH một vài trường thông tin sản phẩm",
        request=ProductSerializer,
        responses={200: ProductSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Xóa sản phẩm",
        description="Xóa một sản phẩm khỏi hệ thống",
        responses={204: OpenApiResponse(description="Deleted successfully")}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

