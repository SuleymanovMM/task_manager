from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ProjectInvitationCreated:
    project_id: UUID
    invitation_id: UUID
    invited_user_id: UUID
    invited_by: UUID
    expires_at: datetime

    def envelope(self):
        return {"event_id": str(uuid4()), "event_type": "ProjectInvitationCreated",
                "occurred_at": datetime.now(timezone.utc).isoformat(), "producer": "project-service", "version": 1,
                "payload": {"project_id": str(self.project_id), "invitation_id": str(self.invitation_id),
                            "invited_user_id": str(self.invited_user_id), "invited_by": str(self.invited_by),
                            "expires_at": self.expires_at.isoformat()}}
