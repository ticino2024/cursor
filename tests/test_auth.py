"""Test authentication endpoints."""

import pytest
from httpx import AsyncClient

from app.db.models.user import User


class TestAuthEndpoints:
    """Test authentication endpoints."""

    async def test_register_user(self, client: AsyncClient):
        """Test user registration."""
        user_data = {
            "email": "newuser@example.com",
            "name": "New User",
            "password": "NewUser123!@#",
        }

        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data
        assert "password_hash" not in data

    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Test registering with duplicate email returns 409."""
        user_data = {
            "email": "test@example.com",
            "name": "Duplicate User",
            "password": "Duplicate123!@#",
        }

        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    async def test_register_invalid_password(self, client: AsyncClient):
        """Test registering with invalid password."""
        user_data = {
            "email": "newuser@example.com",
            "name": "New User",
            "password": "weak",  # Too weak
        }

        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422

    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Test successful login."""
        login_data = {"email": "test@example.com", "password": "Test123!@#"}

        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client: AsyncClient, test_user: User):
        """Test login with invalid credentials."""
        login_data = {"email": "test@example.com", "password": "WrongPassword"}

        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Incorrect" in response.json()["detail"]

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "Test123!@#",
        }

        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401

    async def test_refresh_token(self, client: AsyncClient, test_user: User):
        """Test token refresh."""
        # Login first
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "Test123!@#"},
        )
        tokens = login_response.json()

        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_with_access_token_fails(
        self, client: AsyncClient, test_user: User
    ):
        """Test that refresh fails with access token."""
        # Login first
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "Test123!@#"},
        )
        tokens = login_response.json()

        # Try to refresh with access token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["access_token"]},
        )

        assert response.status_code == 401

    async def test_forgot_password(self, client: AsyncClient, test_user: User):
        """Test password reset request."""
        response = await client.post(
            "/api/v1/auth/forgot-password", json={"email": "test@example.com"}
        )

        assert response.status_code == 200
        assert "message" in response.json()

    async def test_forgot_password_nonexistent_user(self, client: AsyncClient):
        """Test password reset for nonexistent user."""
        response = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "nonexistent@example.com"},
        )

        # Should return 200 to avoid user enumeration
        assert response.status_code == 200
