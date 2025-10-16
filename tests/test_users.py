"""Test user management endpoints."""

import pytest
from httpx import AsyncClient

from app.db.models.user import User


class TestUserEndpoints:
    """Test user management endpoints."""

    async def test_list_users_as_admin(
        self, client: AsyncClient, admin_headers: dict, test_user: User
    ):
        """Test listing users as admin."""
        response = await client.get("/api/v1/users", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert len(data["data"]) > 0

    async def test_list_users_as_regular_user_fails(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that regular users cannot list all users."""
        response = await client.get("/api/v1/users", headers=auth_headers)

        assert response.status_code == 403

    async def test_list_users_without_auth_fails(self, client: AsyncClient):
        """Test that unauthenticated requests fail."""
        response = await client.get("/api/v1/users")

        assert response.status_code == 403

    async def test_get_user_by_id(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """Test getting user by ID."""
        response = await client.get(
            f"/api/v1/users/{test_user.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email

    async def test_get_other_user_as_regular_user_fails(
        self, client: AsyncClient, auth_headers: dict, test_admin: User
    ):
        """Test that regular users cannot view other users."""
        response = await client.get(
            f"/api/v1/users/{test_admin.id}", headers=auth_headers
        )

        assert response.status_code == 403

    async def test_get_other_user_as_admin(
        self, client: AsyncClient, admin_headers: dict, test_user: User
    ):
        """Test that admins can view other users."""
        response = await client.get(
            f"/api/v1/users/{test_user.id}", headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id

    async def test_update_own_profile(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """Test updating own profile."""
        update_data = {"name": "Updated Name"}

        response = await client.put(
            f"/api/v1/users/{test_user.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    async def test_update_own_role_fails(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """Test that users cannot change their own role."""
        update_data = {"role": "admin"}

        response = await client.put(
            f"/api/v1/users/{test_user.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 403

    async def test_admin_can_update_user_role(
        self, client: AsyncClient, admin_headers: dict, test_user: User
    ):
        """Test that admins can update user roles."""
        update_data = {"role": "moderator"}

        response = await client.put(
            f"/api/v1/users/{test_user.id}", json=update_data, headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "moderator"

    async def test_delete_user_as_admin(
        self, client: AsyncClient, admin_headers: dict, test_user: User
    ):
        """Test deleting user as admin."""
        response = await client.delete(
            f"/api/v1/users/{test_user.id}", headers=admin_headers
        )

        assert response.status_code == 200
        assert "message" in response.json()

    async def test_delete_user_as_regular_user_fails(
        self, client: AsyncClient, auth_headers: dict, test_admin: User
    ):
        """Test that regular users cannot delete users."""
        response = await client.delete(
            f"/api/v1/users/{test_admin.id}", headers=auth_headers
        )

        assert response.status_code == 403

    async def test_search_users_as_admin(
        self, client: AsyncClient, admin_headers: dict, test_user: User
    ):
        """Test searching users as admin."""
        response = await client.get(
            "/api/v1/users/search?query=test", headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
