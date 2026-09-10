from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.enums.role import UserRole
from app.infrastructure.database.models.user_model import UserModel


class SQLAlchemyUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            username=model.username,
            password_hash=model.password_hash,
            first_name=model.first_name,
            last_name=model.last_name,
            avatar_url=model.avatar_url,
            role=UserRole(model.role),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, user_id: UUID) -> User | None:
        model = await self.session.get(UserModel, user_id)
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        model = await self.session.scalar(select(UserModel).where(UserModel.email == email))
        return self._to_entity(model) if model else None

    async def get_by_username(self, username: str) -> User | None:
        model = await self.session.scalar(select(UserModel).where(UserModel.username == username))
        return self._to_entity(model) if model else None

    async def create(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            email=user.email,
            username=user.username,
            password_hash=user.password_hash,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def update_password(self, user_id: UUID, password_hash: str) -> None:
        await self.session.execute(update(UserModel).where(UserModel.id == user_id).values(password_hash=password_hash))
