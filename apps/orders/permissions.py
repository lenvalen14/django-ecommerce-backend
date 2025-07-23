from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Chỉ cho phép chủ sở hữu của đơn hàng truy cập.
    Admin thì luôn được phép.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user
