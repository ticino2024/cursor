"""Tests for profile endpoints."""

import pytest
from httpx import AsyncClient


class TestProfile:
    """Test profile endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_profile(self, client: AsyncClient, test_user, user_headers):
        """Test getting current user profile."""
        response = await client.get("/api/v1/profile", headers=user_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
    
    @pytest.mark.asyncio
    async def test_get_profile_unauthorized(self, client: AsyncClient):
        """Test getting profile without authentication."""
        response = await client.get("/api/v1/profile")
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_update_profile(self, client: AsyncClient, test_user, user_headers):
        """Test updating current user profile."""
        update_data = {
            "name": "Updated Profile Name"
        }
        
        response = await client.put(
            "/api/v1/profile",
            json=update_data,
            headers=user_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
    
    @pytest.mark.asyncio
    async def test_change_password(self, client: AsyncClient, test_user, user_headers):
        """Test changing password."""
        password_data = {
            "current_password": "Password123!",
            "new_password": "NewPassword123!"
        }
        
        response = await client.post(
            "/api/v1/profile/change-password",
            json=password_data,
            headers=user_headers
        )
        
        assert response.status_code == 200
        assert "successfully" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, client: AsyncClient, test_user, user_headers):
        """Test changing password with wrong current password."""
        password_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword123!"
        }
        
        response = await client.post(
            "/api/v1/profile/change-password",
            json=password_data,
            headers=user_headers
        )
        
        assert response.status_code == 401
