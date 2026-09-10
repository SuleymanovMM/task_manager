from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ProjectMemberAdded:
    project_id: UUID
    user_id: UUID
    role: str
    added_by: UUID

    def envelope(self):
        return {"event_id": str(uuid4()), "event_type": "ProjectMemberAdded",
                "occurred_at": datetime.now(timezone.utc).isoformat(), "producer": "project-service", "version": 1,
                "payload": {"project_id": str(self.project_id), "user_id": str(self.user_id), "role": self.role,
                            "added_by": str(self.added_by)}}
