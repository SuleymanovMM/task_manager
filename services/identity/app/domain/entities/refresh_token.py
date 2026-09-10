from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class RefreshToken:
    id: UUID
    user_id: UUID
    token_hash: str
    expires_at: datetime
    created_at: datetime
    revoked_at: datetime | None = None

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def revoke(self, revoked_at: datetime) -> None:
        self.revoked_at = revoked_at
