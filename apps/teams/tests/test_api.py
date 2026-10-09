import pytest

from apps.teams.models import Membership
from apps.teams.tests.factories import MembershipFactory, TeamFactory

pytestmark = pytest.mark.django_db


class TestTeamCRUD:
    url = "/api/teams/"

    def test_list_requires_auth(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 401

    def test_list_shows_only_user_teams(self, auth_client, user, other_user):
        # Team, w którym user jest członkiem
        team1 = TeamFactory(owner=user)
        MembershipFactory(team=team1, user=user, role=Membership.Role.OWNER)

        # Team, do którego user NIE należy
        team2 = TeamFactory(owner=other_user)
        MembershipFactory(team=team2, user=other_user, role=Membership.Role.OWNER)

        response = auth_client.get(self.url)

        assert response.status_code == 200
        ids = [t["id"] for t in response.data["results"]]
        assert team1.id in ids
        assert team2.id not in ids

    def test_create_team_adds_owner_membership(self, auth_client, user):
        payload = {"name": "New Team", "description": "Desc"}
        response = auth_client.post(self.url, payload, format="json")

        assert response.status_code == 201
        team_id = response.data["id"]

        membership = Membership.objects.get(team_id=team_id, user=user)
        assert membership.role == Membership.Role.OWNER

    def test_retrieve_returns_memberships(self, auth_client, user):
        team = TeamFactory(owner=user)
        MembershipFactory(team=team, user=user, role=Membership.Role.OWNER)

        response = auth_client.get(f"{self.url}{team.id}/")

        assert response.status_code == 200
        assert "memberships" in response.data
        assert len(response.data["memberships"]) == 1

    def test_destroy_only_owner(self, auth_client, other_auth_client, user, other_user):
        # Team, w którym `user` jest memberem, a `other_user` ownerem
        team = TeamFactory(owner=other_user)
        MembershipFactory(team=team, user=user, role=Membership.Role.MEMBER)
        MembershipFactory(team=team, user=other_user, role=Membership.Role.OWNER)

        # `user` nie jest ownerem — nie może usunąć
        response = auth_client.delete(f"{self.url}{team.id}/")
        assert response.status_code == 403

        # `other_user` jest ownerem — może usunąć
        response = other_auth_client.delete(f"{self.url}{team.id}/")
        assert response.status_code == 204

    def test_retrieve_foreign_team_returns_404(self, auth_client, other_user):
        """User nie widzi teamu, do którego nie należy — dostaje 404."""
        other_team = TeamFactory(owner=other_user)
        MembershipFactory(team=other_team, user=other_user, role=Membership.Role.OWNER)

        response = auth_client.get(f"{self.url}{other_team.id}/")

        assert response.status_code == 404


class TestMembershipManagement:
    def test_add_member(self, auth_client, user, other_user):
        team = TeamFactory(owner=user)
        MembershipFactory(team=team, user=user, role=Membership.Role.OWNER)

        response = auth_client.post(
            f"/api/teams/{team.id}/members/",
            {"user_id": other_user.id, "role": "member"},
            format="json",
        )

        assert response.status_code == 201
        assert Membership.objects.filter(team=team, user=other_user).exists()

    def test_add_duplicate_member(self, auth_client, user, other_user):
        team = TeamFactory(owner=user)
        MembershipFactory(team=team, user=user, role=Membership.Role.OWNER)
        MembershipFactory(team=team, user=other_user, role=Membership.Role.MEMBER)

        response = auth_client.post(
            f"/api/teams/{team.id}/members/",
            {"user_id": other_user.id, "role": "member"},
            format="json",
        )

        assert response.status_code == 400

    def test_remove_member(self, auth_client, user, other_user):
        team = TeamFactory(owner=user)
        MembershipFactory(team=team, user=user, role=Membership.Role.OWNER)
        MembershipFactory(team=team, user=other_user, role=Membership.Role.MEMBER)

        response = auth_client.delete(f"/api/teams/{team.id}/members/{other_user.id}/")

        assert response.status_code == 204
        assert not Membership.objects.filter(team=team, user=other_user).exists()

    def test_cannot_remove_owner(self, auth_client, user):
        team = TeamFactory(owner=user)
        MembershipFactory(team=team, user=user, role=Membership.Role.OWNER)

        response = auth_client.delete(f"/api/teams/{team.id}/members/{user.id}/")

        assert response.status_code == 400
