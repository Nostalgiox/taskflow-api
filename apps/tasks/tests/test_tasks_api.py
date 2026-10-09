import pytest

from apps.tasks.models import Task
from apps.tasks.tests.factories import TaskFactory
from apps.teams.models import Membership
from apps.teams.tests.factories import MembershipFactory, TeamFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def project_for_user(db, user):
    from apps.projects.tests.factories import ProjectFactory

    team = TeamFactory(owner=user)
    MembershipFactory(team=team, user=user, role=Membership.Role.OWNER)
    return ProjectFactory(team=team)


class TestTaskCRUD:
    url = "/api/tasks/"

    def test_create_task_in_own_project(self, auth_client, project_for_user):
        response = auth_client.post(
            self.url,
            {
                "project_id": project_for_user.id,
                "title": "New task",
                "priority": "high",
            },
            format="json",
        )

        assert response.status_code == 201
        assert Task.objects.filter(title="New task").exists()

    def test_create_task_in_foreign_project_forbidden(self, auth_client, other_user):
        from apps.projects.tests.factories import ProjectFactory

        other_team = TeamFactory(owner=other_user)
        MembershipFactory(team=other_team, user=other_user, role=Membership.Role.OWNER)
        other_project = ProjectFactory(team=other_team)

        response = auth_client.post(
            self.url,
            {"project_id": other_project.id, "title": "Hacked"},
            format="json",
        )

        assert response.status_code == 400

    def test_list_only_user_tasks(self, auth_client, project_for_user, other_user):
        from apps.projects.tests.factories import ProjectFactory

        my_task = TaskFactory(project=project_for_user)

        other_team = TeamFactory(owner=other_user)
        MembershipFactory(team=other_team, user=other_user, role=Membership.Role.OWNER)
        other_project = ProjectFactory(team=other_team)
        other_task = TaskFactory(project=other_project)

        response = auth_client.get(self.url)

        ids = [t["id"] for t in response.data["results"]]
        assert my_task.id in ids
        assert other_task.id not in ids

    def test_update_task_as_owner(self, auth_client, project_for_user):
        task = TaskFactory(project=project_for_user)

        response = auth_client.patch(
            f"{self.url}{task.id}/",
            {"status": "done"},
            format="json",
        )

        assert response.status_code == 200
        task.refresh_from_db()
        assert task.status == "done"

    def test_create_task_with_foreign_assignee(
        self, auth_client, user, project_for_user, other_user
    ):
        """Nie można przypisać zadania do kogoś spoza teamu projektu."""
        response = auth_client.post(
            self.url,
            {
                "project_id": project_for_user.id,
                "title": "Bad task",
                "assignee_id": other_user.id,
            },
            format="json",
        )

        assert response.status_code == 400
        assert "assignee_id" in response.data
        assert not Task.objects.filter(title="Bad task").exists()

    def test_create_task_with_valid_assignee(self, auth_client, user, project_for_user):
        """Można przypisać zadanie do członka teamu."""
        response = auth_client.post(
            self.url,
            {
                "project_id": project_for_user.id,
                "title": "Assigned task",
                "assignee_id": user.id,
            },
            format="json",
        )

        assert response.status_code == 201
        assert response.data["assignee"]["id"] == user.id


class TestTaskFilters:
    url = "/api/tasks/"

    def test_filter_by_status(self, auth_client, project_for_user):
        todo = TaskFactory(project=project_for_user, status=Task.Status.TODO)
        done = TaskFactory(project=project_for_user, status=Task.Status.DONE)

        response = auth_client.get(f"{self.url}?status=done")

        ids = [t["id"] for t in response.data["results"]]
        assert done.id in ids
        assert todo.id not in ids

    def test_filter_by_priority(self, auth_client, project_for_user):
        high = TaskFactory(project=project_for_user, priority=Task.Priority.HIGH)
        low = TaskFactory(project=project_for_user, priority=Task.Priority.LOW)

        response = auth_client.get(f"{self.url}?priority=high")

        ids = [t["id"] for t in response.data["results"]]
        assert high.id in ids
        assert low.id not in ids

    def test_filter_assignee_me(self, auth_client, user, project_for_user):
        mine = TaskFactory(project=project_for_user, assignee=user)
        TaskFactory(project=project_for_user, assignee=None)

        response = auth_client.get(f"{self.url}?assignee=me")

        ids = [t["id"] for t in response.data["results"]]
        assert mine.id in ids
        assert len(ids) == 1

    def test_filter_assignee_none(self, auth_client, user, project_for_user):
        TaskFactory(project=project_for_user, assignee=user)
        unassigned = TaskFactory(project=project_for_user, assignee=None)

        response = auth_client.get(f"{self.url}?assignee=none")

        ids = [t["id"] for t in response.data["results"]]
        assert unassigned.id in ids
        assert len(ids) == 1
