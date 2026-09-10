from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pytest
from app.domain.entities.project import Project
from app.domain.entities.project_invitation import ProjectInvitation
from app.domain.enums.project_role import ProjectRole
from app.domain.enums.visibility import Visibility
from app.domain.exceptions.project_exceptions import InvitationExpiredError


def test_project_archive_is_soft_delete():
    p = Project.create(uuid4(), "demo", None, Visibility.PRIVATE, None, None);
    p.archive();
    assert p.status.value == "ARCHIVED"


def test_owner_can_modify_but_manager_cannot():
    uid = uuid4();
    p = Project.create(uid, "demo", None, Visibility.PRIVATE, None, None)
    assert p.can_modify(uid, ProjectRole.OWNER);
    assert not p.can_modify(uid, ProjectRole.MANAGER)


def test_expired_invitation_cannot_be_accepted():
    inv = ProjectInvitation.create(uuid4(), uuid4(), uuid4(), datetime.now(timezone.utc) - timedelta(seconds=1))
    with pytest.raises(InvitationExpiredError): inv.accept()
