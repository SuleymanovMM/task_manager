from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from app.application.services.auth_service import AuthService
from app.core.config import settings
from app.core.security import JWTService, PasswordService, TokenHasher
from app.domain.entities.refresh_token import RefreshToken
from app.domain.entities.user import User
from app.domain.enums.role import UserRole
from app.domain.exceptions.identity_exceptions import InvalidCredentialsError, RefreshTokenRevokedError


class FakeUserRepository:
    def __init__(self) -> None:
        self.users: dict[UUID, User] = {}

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self.users.values() if u.email == email), None)

    async def get_by_username(self, username: str) -> User | None:
        return next((u for u in self.users.values() if u.username == username), None)

    async def create(self, user: User) -> User:
        self.users[user.id] = user
        return user

    async def update_password(self, user_id: UUID, password_hash: str) -> None:
        self.users[user_id].password_hash = password_hash


class FakeRefreshTokenRepository:
    def __init__(self) -> None:
        self.tokens: dict[UUID, RefreshToken] = {}

    async def create(self, token: RefreshToken) -> RefreshToken:
        self.tokens[token.id] = token
        return token

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        return next((t for t in self.tokens.values() if t.token_hash == token_hash), None)

    async def revoke(self, token_id: UUID) -> None:
        self.tokens[token_id].revoke(datetime.now(timezone.utc))

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        for token in self.tokens.values():
            if token.user_id == user_id and token.revoked_at is None:
                token.revoke(datetime.now(timezone.utc))


@pytest.fixture
def auth_service() -> AuthService:
    jwt_service = JWTService.from_files(
        settings.jwt_private_key_path, settings.jwt_public_key_path, settings.jwt_algorithm, settings.app_name
    )
    return AuthService(
        user_repo=FakeUserRepository(),
        refresh_repo=FakeRefreshTokenRepository(),
        password_service=PasswordService(),
        jwt_service=jwt_service,
        access_minutes=15,
        refresh_days=7,
    )


async def _register(auth_service: AuthService, password: str = "password123") -> User:
    return await auth_service.user_repo.create(
        User(
            uuid4(), "user@example.com", "someuser", auth_service.password_service.hash(password),
            None, None, None, UserRole.USER, True, datetime.now(timezone.utc), datetime.now(timezone.utc)
        )
    )


async def test_login_unknown_user_raises_invalid_credentials(auth_service: AuthService):
    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(login="nobody@example.com", password="whatever123")


async def test_login_unknown_user_still_runs_password_verification(auth_service: AuthService, monkeypatch):
    calls: list[str] = []
    original_verify = auth_service.password_service.verify

    def spy_verify(password_hash: str, password: str) -> bool:
        calls.append(password_hash)
        return original_verify(password_hash, password)

    monkeypatch.setattr(auth_service.password_service, "verify", spy_verify)

    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(login="nobody@example.com", password="whatever123")

    assert calls == [auth_service.password_service.dummy_hash]


async def test_refresh_reuse_of_revoked_token_revokes_all_sessions(auth_service: AuthService):
    user = await _register(auth_service)
    pair_a = await auth_service.login(login=user.email, password="password123")
    pair_b = await auth_service.refresh(pair_a.refresh_token)

    with pytest.raises(RefreshTokenRevokedError):
        await auth_service.refresh(pair_a.refresh_token)

    with pytest.raises(RefreshTokenRevokedError):
        await auth_service.refresh(pair_b.refresh_token)


async def test_change_password_revokes_existing_sessions(auth_service: AuthService):
    user = await _register(auth_service)
    pair = await auth_service.login(login=user.email, password="password123")

    await auth_service.change_password(user.id, "password123", "new-password-456")

    with pytest.raises(RefreshTokenRevokedError):
        await auth_service.refresh(pair.refresh_token)
    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(login=user.email, password="password123")
    await auth_service.login(login=user.email, password="new-password-456")


async def test_change_password_rejects_wrong_current_password(auth_service: AuthService):
    user = await _register(auth_service)
    with pytest.raises(InvalidCredentialsError):
        await auth_service.change_password(user.id, "wrong-password", "new-password-456")
