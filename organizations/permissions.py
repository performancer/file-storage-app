from rest_framework import permissions

from users.models import OrganizationUser


class IsInOrganization(permissions.BasePermission):
    """
    This permission class confirms that the user is in an organization.
    The organization does not have to be same with an object.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return OrganizationUser.objects.filter(user=request.user).exists()