import pytest

from apps.projects.models import Project
from apps.projects.tests.factories import ProjectFactory
from apps.teams.models import Membership
from apps.teams.tests.factories import MembershipFactory, TeamFactory

pytestmark = pytest.mark.django_db


class TestProjectCRUD:
    url = "/api/projects/"

    def test_list_only_user_projects(self, auth_client, user, other_user):
        my_team = TeamFactory(owner=user)
        MembershipFactory(team=my_team, user=user, role=Membership.Role.OWNER)
        my_project = ProjectFactory(team=my_team)

        other_team = TeamFactory(owner=other_user)
        MembershipFactory(team=other_team, user=other_user, role=Membership.Role.OWNER)
        other_project = ProjectFactory(team=other_team)

        response = auth_client.get(self.url)

        ids = [p["id"] for p in response.data["results"]]
        assert my_project.id in ids
        assert other_project.id not in ids

    def test_create_project_as_owner(self, auth_client, user):
        team = TeamFactory(owner=user)
        MembershipFactory(team=team, user=user, role=Membership.Role.OWNER)

        response = auth_client.post(
            self.url,
            {"team_id": team.id, "name": "New Project"},
            format="json",
        )

        assert response.status_code == 201
        assert Project.objects.filter(team=team, name="New Project").exists()

    def test_create_project_as_member_forbidden(self, auth_client, user, other_user):
        team = TeamFactory(owner=other_user)
        MembershipFactory(team=team, user=user, role=Membership.Role.MEMBER)
        MembershipFactory(team=team, user=other_user, role=Membership.Role.OWNER)

        response = auth_client.post(
            self.url,
            {"team_id": team.id, "name": "New Project"},
            format="json",
        )

        assert response.status_code == 400

    def test_create_project_in_foreign_team_forbidden(self, auth_client, other_user):
        team = TeamFactory(owner=other_user)
        MembershipFactory(team=team, user=other_user, role=Membership.Role.OWNER)

        response = auth_client.post(
            self.url,
            {"team_id": team.id, "name": "New Project"},
            format="json",
        )

        assert response.status_code == 400

    def test_retrieve_foreign_project_returns_404(self, auth_client, other_user):
        """User nie widzi projektu z cudzego teamu — dostaje 404."""
        other_team = TeamFactory(owner=other_user)
        MembershipFactory(
            team=other_team, user=other_user, role=Membership.Role.OWNER
        )
        other_project = ProjectFactory(team=other_team)

        response = auth_client.get(f"{self.url}{other_project.id}/")

        assert response.status_code == 404

    def test_update_foreign_project_returns_404(self, auth_client, other_user):
        """User nie może edytować cudzego projektu."""
        other_team = TeamFactory(owner=other_user)
        MembershipFactory(
            team=other_team, user=other_user, role=Membership.Role.OWNER
        )
        other_project = ProjectFactory(team=other_team)

        response = auth_client.patch(
            f"{self.url}{other_project.id}/",
            {"name": "Hacked"},
            format="json",
        )

        assert response.status_code == 404


class TestProjectFilters:
    url = "/api/projects/"

    def test_filter_by_status(self, auth_client, user):
        team = TeamFactory(owner=user)
        MembershipFactory(team=team, user=user, role=Membership.Role.OWNER)
        active = ProjectFactory(team=team, status=Project.Status.ACTIVE)
        archived = ProjectFactory(team=team, status=Project.Status.ARCHIVED)

        response = auth_client.get(f"{self.url}?status=archived")

        ids = [p["id"] for p in response.data["results"]]
        assert archived.id in ids
        assert active.id not in ids

    def test_search_by_name(self, auth_client, user):
        team = TeamFactory(owner=user)
        MembershipFactory(team=team, user=user, role=Membership.Role.OWNER)
        match = ProjectFactory(team=team, name="Unique Name")
        ProjectFactory(team=team, name="Other")

        response = auth_client.get(f"{self.url}?search=Unique")

        ids = [p["id"] for p in response.data["results"]]
        assert match.id in ids
        assert len(ids) == 1