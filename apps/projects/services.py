from django.db import transaction
from rest_framework.exceptions import PermissionDenied

from apps.teams.models import Membership, Team

from .models import Project


@transaction.atomic
def create_project(*, user, team: Team, name: str, description: str = "") -> Project:
    """Tworzy projekt. Tylko owner/admin teamu może tworzyć."""
    is_admin = Membership.objects.filter(
        team=team,
        user=user,
        role__in=[Membership.Role.OWNER, Membership.Role.ADMIN],
    ).exists()

    if not is_admin:
        raise PermissionDenied("You must be an owner or admin of this team.")

    return Project.objects.create(
        team=team,
        name=name,
        description=description,
    )