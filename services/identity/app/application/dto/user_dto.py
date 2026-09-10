from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums.role import UserRole


@dataclass(frozen=True, slots=True)
class UserDTO:
    id: UUID
    email: str
    username: str
    first_name: str | None
    last_name: str | None
    avatar_url: str | None
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class TokenPairDTO:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
