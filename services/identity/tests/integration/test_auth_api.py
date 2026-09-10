import jwt
from pathlib import Path

import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.fixture
def register_payload():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
    }


async def test_register_creates_user(client: AsyncClient, register_payload: dict):
    response = await client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == register_payload["email"]
    assert data["username"] == register_payload["username"]
    assert "password" not in data
    assert "password_hash" not in data


async def test_login_returns_tokens(client: AsyncClient, register_payload: dict):
    await client.post("/api/v1/auth/register", json=register_payload)
    response = await client.post(
        "/api/v1/auth/login",
        json={"login": register_payload["email"], "password": register_payload["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]


async def test_login_invalid_password(client: AsyncClient, register_payload: dict):
    await client.post("/api/v1/auth/register", json=register_payload)
    response = await client.post(
        "/api/v1/auth/login",
        json={"login": register_payload["email"], "password": "wrong-password"},
    )
    assert response.status_code == 401


async def test_refresh_issues_new_tokens(client: AsyncClient, register_payload: dict):
    await client.post("/api/v1/auth/register", json=register_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"login": register_payload["email"], "password": register_payload["password"]},
    )
    refresh_token = login.json()["refresh_token"]
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["refresh_token"] != refresh_token


async def test_refresh_revoked_token(client: AsyncClient, register_payload: dict):
    await client.post("/api/v1/auth/register", json=register_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"login": register_payload["email"], "password": register_payload["password"]},
    )
    tokens = login.json()
    await client.post("/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 401


async def test_logout_returns_204(client: AsyncClient, register_payload: dict):
    await client.post("/api/v1/auth/register", json=register_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"login": register_payload["email"], "password": register_payload["password"]},
    )
    response = await client.post("/api/v1/auth/logout", json={"refresh_token": login.json()["refresh_token"]})
    assert response.status_code == 204


async def test_me_returns_current_user(client: AsyncClient, register_payload: dict):
    await client.post("/api/v1/auth/register", json=register_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"login": register_payload["email"], "password": register_payload["password"]},
    )
    access_token = login.json()["access_token"]
    response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == register_payload["email"]


async def test_me_without_token(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_jwt_claims(client: AsyncClient, register_payload: dict):
    await client.post("/api/v1/auth/register", json=register_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"login": register_payload["email"], "password": register_payload["password"]},
    )
    token = login.json()["access_token"]
    payload = jwt.decode(
        token,
        Path(settings.jwt_public_key_path).read_text(),
        algorithms=[settings.jwt_algorithm],
    )
    for claim in ("sub", "role", "iss", "iat", "exp", "jti"):
        assert claim in payload


async def test_login_nonexistent_user_returns_401(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login", json={"login": "nobody@example.com", "password": "whatever123"}
    )
    assert response.status_code == 401


async def test_login_rate_limited_after_threshold(client: AsyncClient, register_payload: dict):
    await client.post("/api/v1/auth/register", json=register_payload)
    payload = {"login": register_payload["email"], "password": "wrong-password"}
    for _ in range(10):
        response = await client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == 401
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 429


async def test_refresh_reuse_revokes_all_sessions(client: AsyncClient, register_payload: dict):
    await client.post("/api/v1/auth/register", json=register_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"login": register_payload["email"], "password": register_payload["password"]},
    )
    stolen_token = login.json()["refresh_token"]

    first_use = await client.post("/api/v1/auth/refresh", json={"refresh_token": stolen_token})
    assert first_use.status_code == 200
    rotated_token = first_use.json()["refresh_token"]

    replay = await client.post("/api/v1/auth/refresh", json={"refresh_token": stolen_token})
    assert replay.status_code == 401

    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": rotated_token})
    assert response.status_code == 401


async def test_logout_all_revokes_every_session(client: AsyncClient, register_payload: dict):
    await client.post("/api/v1/auth/register", json=register_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"login": register_payload["email"], "password": register_payload["password"]},
    )
    tokens = login.json()

    logout_all_response = await client.post(
        "/api/v1/auth/logout-all", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert logout_all_response.status_code == 204

    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 401


async def test_change_password_updates_credentials_and_revokes_sessions(
    client: AsyncClient, register_payload: dict
):
    await client.post("/api/v1/auth/register", json=register_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"login": register_payload["email"], "password": register_payload["password"]},
    )
    tokens = login.json()

    response = await client.post(
        "/api/v1/auth/password/change",
        json={"current_password": register_payload["password"], "new_password": "new-password-456"},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 204

    stale_refresh = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert stale_refresh.status_code == 401

    old_password_login = await client.post(
        "/api/v1/auth/login",
        json={"login": register_payload["email"], "password": register_payload["password"]},
    )
    assert old_password_login.status_code == 401

    new_password_login = await client.post(
        "/api/v1/auth/login",
        json={"login": register_payload["email"], "password": "new-password-456"},
    )
    assert new_password_login.status_code == 200


async def test_change_password_rejects_wrong_current_password(client: AsyncClient, register_payload: dict):
    await client.post("/api/v1/auth/register", json=register_payload)
    login = await client.post(
        "/api/v1/auth/login",
        json={"login": register_payload["email"], "password": register_payload["password"]},
    )
    access_token = login.json()["access_token"]

    response = await client.post(
        "/api/v1/auth/password/change",
        json={"current_password": "wrong-password", "new_password": "new-password-456"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 401
