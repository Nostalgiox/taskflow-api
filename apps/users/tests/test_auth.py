import pytest

pytestmark = pytest.mark.django_db


class TestRegister:
    url = "/api/auth/register/"

    def test_register_success(self, api_client):
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "strongpass123",
            "password_confirm": "strongpass123",
        }
        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == 201
        assert response.data["username"] == "newuser"
        assert "password" not in response.data

    def test_register_password_mismatch(self, api_client):
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "strongpass123",
            "password_confirm": "different123",
        }
        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == 400
        assert "password" in response.data

    def test_register_duplicate_username(self, api_client, user):
        payload = {
            "username": user.username,
            "email": "another@example.com",
            "password": "strongpass123",
            "password_confirm": "strongpass123",
        }
        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == 400


class TestLogin:
    url = "/api/auth/login/"

    def test_login_success(self, api_client, user):
        response = api_client.post(
            self.url,
            {"username": user.username, "password": "test12345"},
            format="json",
        )

        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_wrong_password(self, api_client, user):
        response = api_client.post(
            self.url,
            {"username": user.username, "password": "wrong"},
            format="json",
        )

        assert response.status_code == 401


class TestMe:
    url = "/api/auth/me/"

    def test_me_requires_auth(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 401

    def test_me_returns_user(self, auth_client, user):
        response = auth_client.get(self.url)

        assert response.status_code == 200
        assert response.data["username"] == user.username
        assert response.data["email"] == user.email
