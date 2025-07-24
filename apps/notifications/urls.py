from django.urls import path
from .views import (NotificationListView,
                    MarkNotificationAsReadView,
                    UnreadNotificationCountView, MarkAllNotificationAsReadView)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/mark-as-read/', MarkNotificationAsReadView.as_view(), name='notification-mark-read'),
    path('mark-all-as-read/', MarkAllNotificationAsReadView.as_view(), name='notification-mark-all-read'),
    path('unread-count/', UnreadNotificationCountView.as_view(), name='notification-unread-count'),
]
