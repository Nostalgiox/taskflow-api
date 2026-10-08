from rest_framework import permissions

from apps.teams.models import Membership


class IsTaskProjectMember(permissions.BasePermission):
    """Dostęp tylko dla członka teamu, do którego należy projekt zadania."""

    def has_object_permission(self, request, view, obj):
        task = getattr(obj, "task", obj)
        return Membership.objects.filter(
            team=task.project.team,
            user=request.user,
        ).exists()


class IsTaskProjectAdmin(permissions.BasePermission):
    """Edycja/usuwanie zadania — tylko owner/admin teamu."""

    def has_object_permission(self, request, view, obj):
        return Membership.objects.filter(
            team=obj.project.team,
            user=request.user,
            role__in=[Membership.Role.OWNER, Membership.Role.ADMIN],
        ).exists()


class IsCommentAuthor(permissions.BasePermission):
    """Usuwanie komentarza — tylko autor lub owner/admin teamu."""

    def has_object_permission(self, request, view, obj):
        if obj.author == request.user:
            return True

        return Membership.objects.filter(
            team=obj.task.project.team,
            user=request.user,
            role__in=[Membership.Role.OWNER, Membership.Role.ADMIN],
        ).exists()