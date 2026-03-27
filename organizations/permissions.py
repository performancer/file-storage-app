from rest_framework import permissions

from users.models import OrganizationUser


class IsInOrganization(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return OrganizationUser.objects.filter(user=request.user).exists()