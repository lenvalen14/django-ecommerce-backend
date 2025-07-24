from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.renderers import CustomResponseRenderer
from .models import Notification
from .serializers import NotificationSerializer

@extend_schema(tags=["Notifications"])
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    renderer_classes = [CustomResponseRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        is_read = self.request.content_params.get("is_read")
        if is_read in ['true', 'false']:
            qs = qs.filter(is_read=(is_read == 'true'))
        return qs

@extend_schema(tags=["Notifications"])
class MarkNotificationAsReadView(APIView):
    renderer_classes = [CustomResponseRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            notif = Notification.objects.get(id=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found"}, status=404)

        notif.is_read = True
        notif.save()
        return Response({"message": "Marked as read"}, status=status.HTTP_200_OK)

@extend_schema(tags=["Notifications"])
class MarkAllNotificationAsReadView(APIView):
    renderer_classes = [CustomResponseRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        updated_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({
            "message": f"{updated_count} notifications marked as read."
        }, status=status.HTTP_200_OK)

@extend_schema(tags=["Notifications"])
class UnreadNotificationCountView(APIView):
    renderer_classes = [CustomResponseRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread_count": count})
