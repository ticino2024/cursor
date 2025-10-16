"""Test profile endpoints."""

import pytest
from httpx import AsyncClient
from io import BytesIO

from app.db.models.user import User


class TestProfileEndpoints:
    """Test profile endpoints."""

    async def test_get_profile(self, client: AsyncClient, auth_headers: dict, test_user: User):
        """Test getting own profile."""
        response = await client.get("/api/v1/profile", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email

    async def test_get_profile_without_auth_fails(self, client: AsyncClient):
        """Test that unauthenticated requests fail."""
        response = await client.get("/api/v1/profile")

        assert response.status_code == 403

    async def test_update_profile(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """Test updating own profile."""
        update_data = {"name": "Updated Profile Name"}

        response = await client.put(
            "/api/v1/profile", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Profile Name"

    async def test_update_profile_email(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating profile email."""
        update_data = {"email": "newemail@example.com"}

        response = await client.put(
            "/api/v1/profile", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newemail@example.com"

    async def test_update_profile_role_fails(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that users cannot change their own role via profile."""
        update_data = {"role": "admin"}

        response = await client.put(
            "/api/v1/profile", json=update_data, headers=auth_headers
        )

        assert response.status_code == 403

    async def test_upload_avatar(self, client: AsyncClient, auth_headers: dict):
        """Test uploading profile avatar."""
        # Create a fake image file
        fake_image = BytesIO(b"fake image content")
        files = {"file": ("avatar.jpg", fake_image, "image/jpeg")}

        response = await client.post(
            "/api/v1/profile/avatar", files=files, headers=auth_headers
        )

        assert response.status_code == 200
        assert "message" in response.json()

    async def test_upload_avatar_invalid_type(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test uploading invalid file type."""
        fake_file = BytesIO(b"fake pdf content")
        files = {"file": ("document.pdf", fake_file, "application/pdf")}

        response = await client.post(
            "/api/v1/profile/avatar", files=files, headers=auth_headers
        )

        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    async def test_upload_avatar_too_large(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test uploading file that's too large."""
        # Create a file larger than 5MB
        large_file = BytesIO(b"x" * (6 * 1024 * 1024))
        files = {"file": ("large.jpg", large_file, "image/jpeg")}

        response = await client.post(
            "/api/v1/profile/avatar", files=files, headers=auth_headers
        )

        assert response.status_code == 400
        assert "exceeds" in response.json()["detail"]
