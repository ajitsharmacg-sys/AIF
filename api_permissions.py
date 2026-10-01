from rest_framework import permissions
from aif.roles import ROLES
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class IsApplicationUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=ROLES).exists()
