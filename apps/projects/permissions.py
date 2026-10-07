from rest_framework import permissions

from apps.teams.models import Membership


class IsProjectTeamMember(permissions.BasePermission):
    """Widzi projekt tylko członek teamu, do którego projekt należy."""

    def has_object_permission(self, request, view, obj):
        return Membership.objects.filter(
            team=obj.team,
            user=request.user,
        ).exists()


class IsProjectTeamAdmin(permissions.BasePermission):
    """Edytować/usuwać może tylko owner/admin teamu."""

    def has_object_permission(self, request, view, obj):
        return Membership.objects.filter(
            team=obj.team,
            user=request.user,
            role__in=[Membership.Role.OWNER, Membership.Role.ADMIN],
        ).exists()