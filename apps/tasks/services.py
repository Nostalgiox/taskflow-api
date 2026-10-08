from django.db import transaction
from rest_framework.exceptions import PermissionDenied

from apps.teams.models import Membership

from .models import Comment, Task


@transaction.atomic
def create_task(*, user, project, title: str, **kwargs) -> Task:
    """Tworzy zadanie. Tylko członek teamu projektu może tworzyć."""
    is_member = Membership.objects.filter(
        team=project.team,
        user=user,
    ).exists()

    if not is_member:
        raise PermissionDenied("You must be a member of the project's team.")

    return Task.objects.create(project=project, title=title, **kwargs)


@transaction.atomic
def add_comment(*, user, task: Task, content: str) -> Comment:
    """Dodaje komentarz. Tylko członek teamu może komentować."""
    is_member = Membership.objects.filter(
        team=task.project.team,
        user=user,
    ).exists()

    if not is_member:
        raise PermissionDenied("You must be a member of the project's team.")

    return Comment.objects.create(task=task, author=user, content=content)