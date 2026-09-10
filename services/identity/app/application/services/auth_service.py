from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from app.application.dto.user_dto import TokenPairDTO, UserDTO
from app.core.security import JWTService, PasswordService, TokenHasher, generate_refresh_token
from app.domain.entities.refresh_token import RefreshToken
from app.domain.entities.user import User
from app.domain.enums.role import UserRole
from app.domain.exceptions.identity_exceptions import (
    InvalidCredentialsError,
    RefreshTokenExpiredError,
    RefreshTokenRevokedError,
    UserAlreadyExistsError,
    UserNotFoundError,
)


class AuthService:
    def __init__(
            self, user_repo, refresh_repo, password_service: PasswordService, jwt_service: JWTService,
            access_minutes: int, refresh_days: int
    ):
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo
        self.password_service = password_service
        self.jwt_service = jwt_service
        self.access_minutes = access_minutes
        self.refresh_days = refresh_days

    @staticmethod
    def _user_dto(user: User) -> UserDTO:
        return UserDTO(user.id, user.email, user.username, user.first_name, user.last_name, user.avatar_url, user.role,
                       user.is_active, user.created_at, user.updated_at)

    async def register(self, *, email: str, username: str, password: str, first_name: str | None = None,
                       last_name: str | None = None, avatar_url: str | None = None) -> UserDTO:
        if await self.user_repo.get_by_email(email.lower()) or await self.user_repo.get_by_username(username):
            raise UserAlreadyExistsError()
        now = datetime.now(timezone.utc)
        user = User(uuid4(), email.lower(), username, self.password_service.hash(password), first_name, last_name,
                    avatar_url, UserRole.USER, True, now, now)
        return self._user_dto(await self.user_repo.create(user))

    async def login(self, *, login: str, password: str) -> TokenPairDTO:
        user = await self.user_repo.get_by_email(login.lower()) or await self.user_repo.get_by_username(login)
        password_hash = user.password_hash if user else self.password_service.dummy_hash
        password_valid = self.password_service.verify(password_hash, password)
        if not user or not user.is_active or not password_valid:
            raise InvalidCredentialsError()
        return await self._issue_pair(user)

    async def refresh(self, refresh_token: str) -> TokenPairDTO:
        record = await self.refresh_repo.get_by_hash(TokenHasher.hash(refresh_token))
        if not record:
            raise RefreshTokenRevokedError("Refresh token is invalid")
        if record.revoked_at is not None:
            # Повторное использование отозванного токена — признак кражи: рвём все сессии.
            await self.refresh_repo.revoke_all_for_user(record.user_id)
            raise RefreshTokenRevokedError()
        if record.expires_at <= datetime.now(timezone.utc):
            raise RefreshTokenExpiredError()
        user = await self.user_repo.get_by_id(record.user_id)
        if not user or not user.is_active:
            raise InvalidCredentialsError()
        await self.refresh_repo.revoke(record.id)
        return await self._issue_pair(user)

    async def logout(self, refresh_token: str) -> None:
        record = await self.refresh_repo.get_by_hash(TokenHasher.hash(refresh_token))
        if record and record.revoked_at is None:
            await self.refresh_repo.revoke(record.id)

    async def logout_all(self, user_id: UUID) -> None:
        await self.refresh_repo.revoke_all_for_user(user_id)

    async def change_password(self, user_id: UUID, current_password: str, new_password: str) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active or not self.password_service.verify(user.password_hash, current_password):
            raise InvalidCredentialsError()
        await self.user_repo.update_password(user_id, self.password_service.hash(new_password))
        await self.refresh_repo.revoke_all_for_user(user_id)

    async def get_user(self, user_id: UUID) -> UserDTO:
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UserNotFoundError()
        return self._user_dto(user)

    async def _issue_pair(self, user: User) -> TokenPairDTO:
        access = self.jwt_service.create_access_token(user.id, user.role.value, self.access_minutes)
        refresh = generate_refresh_token()
        now = datetime.now(timezone.utc)
        entity = RefreshToken(uuid4(), user.id, TokenHasher.hash(refresh), now + timedelta(days=self.refresh_days), now)
        await self.refresh_repo.create(entity)
        return TokenPairDTO(access, refresh)
