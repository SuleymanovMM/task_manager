from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums.role import UserRole


@dataclass(slots=True)
class User:
    id: UUID
    email: str
    username: str
    password_hash: str
    first_name: str | None
    last_name: str | None
    avatar_url: str | None
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
