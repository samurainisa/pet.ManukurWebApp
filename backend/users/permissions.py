from rest_framework.permissions import BasePermission

from users.models import UserProfile
from users.utils import get_user_role


class IsMasterRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and get_user_role(request.user) == UserProfile.Role.MASTER
        )


class IsClientRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and get_user_role(request.user) == UserProfile.Role.CLIENT
        )
