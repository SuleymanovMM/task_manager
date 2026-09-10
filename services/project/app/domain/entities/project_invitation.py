from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from app.domain.enums.invitation_status import InvitationStatus
from app.domain.exceptions.project_exceptions import InvitationExpiredError, InvalidInvitationStatusError


@dataclass
class ProjectInvitation:
    id: UUID
    project_id: UUID
    invited_user_id: UUID
    invited_by: UUID
    status: InvitationStatus
    expires_at: datetime
    created_at: datetime

    @classmethod
    def create(cls, project_id, invited_user_id, invited_by, expires_at):
        return cls(uuid4(), project_id, invited_user_id, invited_by, InvitationStatus.PENDING, expires_at,
                   datetime.now(timezone.utc))

    def accept(self):
        if self.status != InvitationStatus.PENDING:
            raise InvalidInvitationStatusError()
        now = datetime.now(timezone.utc)
        if self.expires_at <= now:
            self.status = InvitationStatus.EXPIRED
            raise InvitationExpiredError()
        self.status = InvitationStatus.ACCEPTED

    def decline(self):
        if self.status != InvitationStatus.PENDING:
            raise InvalidInvitationStatusError()
        self.status = InvitationStatus.DECLINED
