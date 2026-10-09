from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import Membership, Team

User = get_user_model()


@transaction.atomic
def create_team(*, owner, name: str, description: str = "") -> Team:
    """Tworzy team i automatycznie dodaje ownera jako członka z rolą OWNER."""
    team = Team.objects.create(
        name=name,
        description=description,
        owner=owner,
    )
    Membership.objects.create(
        team=team,
        user=owner,
        role=Membership.Role.OWNER,
    )
    return team


@transaction.atomic
def add_member(*, team: Team, user_id: int, role: str) -> Membership:
    """Dodaje członka do teamu. Podnosi błąd, jeśli już istnieje."""
    user = User.objects.get(id=user_id)

    if Membership.objects.filter(team=team, user=user).exists():
        raise ValidationError({"user_id": "User is already a member of this team."})

    if user == team.owner and role != Membership.Role.OWNER:
        raise ValidationError({"role": "Owner must have the owner role."})

    return Membership.objects.create(team=team, user=user, role=role)


@transaction.atomic
def remove_member(*, team: Team, user_id: int) -> None:
    """Usuwa członka z teamu. Nie można usunąć ownera."""
    if team.owner_id == user_id:
        raise ValidationError({"user_id": "Cannot remove the team owner."})

    Membership.objects.filter(team=team, user_id=user_id).delete()
