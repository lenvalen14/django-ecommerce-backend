from rest_framework_nested import routers
from apps.products.views import ProductViewSet, CategoryViewSet
from django.urls import path, include

# Router gốc
router = routers.DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'categories', CategoryViewSet, basename='categories')

# Nested router: /categories/{category_pk}/products/
category_products_router = routers.NestedSimpleRouter(router, r'categories', lookup='category')
category_products_router.register(r'products', ProductViewSet, basename='category-products')

# Kết hợp URLs
urlpatterns = [
    path('', include(router.urls)),
    path('', include(category_products_router.urls)),
]
