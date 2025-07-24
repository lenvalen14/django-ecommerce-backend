from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('api/v1/', include([
        path("admin/", admin.site.urls),
        path('', include('apps.products.urls')),
        path('', include('apps.users.urls')),
        path('', include('apps.orders.urls')),
        path('', include('apps.notifications.urls')),
        path('schema/', SpectacularAPIView.as_view(), name='schema'),
        path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ])),
]
