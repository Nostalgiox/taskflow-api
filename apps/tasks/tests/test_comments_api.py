import pytest

from apps.tasks.models import Comment
from apps.tasks.tests.factories import TaskFactory
from apps.teams.models import Membership
from apps.teams.tests.factories import MembershipFactory, TeamFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def task_for_user(db, user):
    from apps.projects.tests.factories import ProjectFactory

    team = TeamFactory(owner=user)
    MembershipFactory(team=team, user=user, role=Membership.Role.OWNER)
    project = ProjectFactory(team=team)
    return TaskFactory(project=project)


class TestComments:
    def test_add_comment(self, auth_client, user, task_for_user):
        response = auth_client.post(
            f"/api/tasks/{task_for_user.id}/comments/",
            {"content": "Looks good!"},
            format="json",
        )

        assert response.status_code == 201
        assert response.data["content"] == "Looks good!"
        assert response.data["author"]["username"] == user.username
        assert Comment.objects.filter(task=task_for_user, author=user).exists()

    def test_list_comments(self, auth_client, task_for_user):
        from apps.tasks.tests.factories import CommentFactory

        CommentFactory(task=task_for_user, content="First")
        CommentFactory(task=task_for_user, content="Second")

        response = auth_client.get(f"/api/tasks/{task_for_user.id}/comments/")

        assert response.status_code == 200
        assert len(response.data) == 2

    def test_task_detail_includes_comments(self, auth_client, task_for_user):
        from apps.tasks.tests.factories import CommentFactory

        CommentFactory(task=task_for_user, content="Nice")

        response = auth_client.get(f"/api/tasks/{task_for_user.id}/")

        assert response.status_code == 200
        assert "comments" in response.data
        assert len(response.data["comments"]) == 1

    def test_delete_own_comment(self, auth_client, user, task_for_user):
        from apps.tasks.tests.factories import CommentFactory

        comment = CommentFactory(task=task_for_user, author=user)

        response = auth_client.delete(f"/api/comments/{comment.id}/")

        assert response.status_code == 204
        assert not Comment.objects.filter(id=comment.id).exists()

    def test_cannot_comment_on_foreign_task(self, auth_client, other_user):
        from apps.projects.tests.factories import ProjectFactory

        other_team = TeamFactory(owner=other_user)
        MembershipFactory(team=other_team, user=other_user, role=Membership.Role.OWNER)
        other_project = ProjectFactory(team=other_team)
        foreign_task = TaskFactory(project=other_project)

        response = auth_client.post(
            f"/api/tasks/{foreign_task.id}/comments/",
            {"content": "Hacked"},
            format="json",
        )

        assert response.status_code == 404
