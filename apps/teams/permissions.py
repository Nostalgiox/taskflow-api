from rest_framework import permissions

from .models import Membership


class IsTeamMember(permissions.BasePermission):
    """Dostęp tylko dla członków teamu."""

    def has_object_permission(self, request, view, obj):
        team = getattr(obj, "team", obj)
        return Membership.objects.filter(team=team, user=request.user).exists()


class IsTeamAdmin(permissions.BasePermission):
    """Dostęp tylko dla ownera lub admina teamu."""

    def has_object_permission(self, request, view, obj):
        team = getattr(obj, "team", obj)
        return Membership.objects.filter(
            team=team,
            user=request.user,
            role__in=[Membership.Role.OWNER, Membership.Role.ADMIN],
        ).exists()


class IsTeamOwner(permissions.BasePermission):
    """Dostęp tylko dla ownera teamu."""

    def has_object_permission(self, request, view, obj):
        team = getattr(obj, "team", obj)
        return Membership.objects.filter(
            team=team,
            user=request.user,
            role=Membership.Role.OWNER,
        ).exists()
