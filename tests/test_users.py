"""Tests for user management endpoints."""

import pytest
from httpx import AsyncClient


class TestUsers:
    """Test user management endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_users_as_admin(self, client: AsyncClient, test_user, test_admin, admin_headers):
        """Test listing users as admin."""
        response = await client.get("/api/v1/users", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["data"]) >= 2  # At least test_user and test_admin
    
    @pytest.mark.asyncio
    async def test_list_users_as_regular_user(self, client: AsyncClient, test_user, user_headers):
        """Test that regular users cannot list all users."""
        response = await client.get("/api/v1/users", headers=user_headers)
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_list_users_unauthorized(self, client: AsyncClient):
        """Test listing users without authentication."""
        response = await client.get("/api/v1/users")
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, client: AsyncClient, test_user, user_headers):
        """Test getting user by ID."""
        response = await client.get(f"/api/v1/users/{test_user.id}", headers=user_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, client: AsyncClient, user_headers):
        """Test getting nonexistent user."""
        response = await client.get("/api/v1/users/nonexistent-id", headers=user_headers)
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_user_as_admin(self, client: AsyncClient, admin_headers):
        """Test creating user as admin."""
        user_data = {
            "email": "created@example.com",
            "name": "Created User",
            "password": "Password123!"
        }
        
        response = await client.post("/api/v1/users", json=user_data, headers=admin_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
    
    @pytest.mark.asyncio
    async def test_create_user_as_regular_user(self, client: AsyncClient, user_headers):
        """Test that regular users cannot create users."""
        user_data = {
            "email": "created@example.com",
            "name": "Created User",
            "password": "Password123!"
        }
        
        response = await client.post("/api/v1/users", json=user_data, headers=user_headers)
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_update_own_user(self, client: AsyncClient, test_user, user_headers):
        """Test updating own user information."""
        update_data = {
            "name": "Updated Name"
        }
        
        response = await client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=user_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
    
    @pytest.mark.asyncio
    async def test_update_other_user_as_regular_user(
        self,
        client: AsyncClient,
        test_user,
        test_admin,
        user_headers
    ):
        """Test that regular users cannot update other users."""
        update_data = {
            "name": "Hacked Name"
        }
        
        response = await client.put(
            f"/api/v1/users/{test_admin.id}",
            json=update_data,
            headers=user_headers
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_update_user_as_admin(self, client: AsyncClient, test_user, admin_headers):
        """Test updating user as admin."""
        update_data = {
            "name": "Admin Updated Name"
        }
        
        response = await client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
    
    @pytest.mark.asyncio
    async def test_delete_own_user(self, client: AsyncClient, test_user, user_headers):
        """Test deleting own user."""
        response = await client.delete(f"/api/v1/users/{test_user.id}", headers=user_headers)
        
        assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_delete_other_user_as_regular_user(
        self,
        client: AsyncClient,
        test_user,
        test_admin,
        user_headers
    ):
        """Test that regular users cannot delete other users."""
        response = await client.delete(f"/api/v1/users/{test_admin.id}", headers=user_headers)
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_search_users_as_admin(self, client: AsyncClient, test_user, admin_headers):
        """Test searching users as admin."""
        response = await client.get(
            "/api/v1/users/search",
            params={"q": "test"},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
