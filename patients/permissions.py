from rest_framework import permissions


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow creators of an object or staff to edit/delete it.
    Authenticated users can view details.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the creator or staff
        return obj.created_by == request.user or request.user.is_staff
