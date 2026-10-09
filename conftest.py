import pytest
from rest_framework.test import APIClient

from apps.teams.models import Membership, Team
from apps.users.models import User


@pytest.fixture
def api_client() -> APIClient:
    """Niezalogowany klient API."""
    return APIClient()


@pytest.fixture
def user(db) -> User:
    """Podstawowy użytkownik."""
    return User.objects.create_user(
        username="dawid",
        email="dawid@example.com",
        password="test12345",
    )


@pytest.fixture
def other_user(db) -> User:
    """Drugi użytkownik (do testów uprawnień)."""
    return User.objects.create_user(
        username="other",
        email="other@example.com",
        password="test12345",
    )


@pytest.fixture
def auth_client(api_client: APIClient, user: User) -> APIClient:
    """Klient API zalogowany jako `user` przez JWT."""
    response = api_client.post(
        "/api/auth/login/",
        {"username": user.username, "password": "test12345"},
        format="json",
    )
    token = response.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


@pytest.fixture
def other_auth_client(api_client: APIClient, other_user: User) -> APIClient:
    """Klient API zalogowany jako `other_user`."""
    client = APIClient()
    response = client.post(
        "/api/auth/login/",
        {"username": other_user.username, "password": "test12345"},
        format="json",
    )
    token = response.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def team(db, user: User) -> Team:
    """Team, w którym `user` jest ownerem."""
    team = Team.objects.create(
        name="Test Team",
        owner=user,
    )
    Membership.objects.create(
        team=team,
        user=user,
        role=Membership.Role.OWNER,
    )
    return team