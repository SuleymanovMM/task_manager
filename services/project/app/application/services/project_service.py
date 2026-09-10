from datetime import datetime, timedelta, timezone
from app.domain.entities.project import Project
from app.domain.entities.project_member import ProjectMember
from app.domain.entities.project_invitation import ProjectInvitation
from app.domain.enums.project_role import ProjectRole
from app.domain.enums.project_status import ProjectStatus
from app.domain.exceptions.project_exceptions import (
    CannotInviteSelfError,
    InvitationNotFoundError,
    MemberAlreadyExistsError,
    ProjectAccessDeniedError,
    ProjectAlreadyArchivedError,
    ProjectNotFoundError,
)
from app.domain.events.project_member_added import ProjectMemberAdded
from app.domain.events.project_invitation_created import ProjectInvitationCreated


class ProjectService:
    def __init__(self, projects, teams, invitations, publisher):
        self.projects = projects
        self.teams = teams
        self.invitations = invitations
        self.publisher = publisher

    async def create_project(self, actor_id, req):
        project = Project.create(actor_id, req.name, req.description, req.visibility, req.start_date, req.deadline)
        await self.projects.create(project)
        await self.projects.add_member(ProjectMember.create(project.id, actor_id, ProjectRole.OWNER))
        return project

    async def get_project(self, project_id, actor_id):
        project = await self.projects.get(project_id)
        if not project:
            raise ProjectNotFoundError()
        member = await self.projects.get_member(project_id, actor_id)
        if not member:
            raise ProjectAccessDeniedError()
        return project

    async def list_projects(self, actor_id, offset, limit):
        return await self.projects.list_for_user(actor_id, offset, limit)

    async def update_project(self, project_id, actor_id, req):
        project = await self.get_project(project_id, actor_id)
        member = await self.projects.get_member(project_id, actor_id)
        if not project.can_modify(actor_id, member.role):
            raise ProjectAccessDeniedError()
        if project.status == ProjectStatus.ARCHIVED:
            raise ProjectAlreadyArchivedError()
        for field, value in req.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        project.updated_at = datetime.now(timezone.utc)
        return await self.projects.update(project)

    async def archive_project(self, project_id, actor_id):
        project = await self.get_project(project_id, actor_id)
        member = await self.projects.get_member(project_id, actor_id)
        if not project.can_modify(actor_id, member.role):
            raise ProjectAccessDeniedError()
        project.archive()
        await self.projects.update(project)

    async def add_member(self, project_id, actor_id, user_id, role):
        project = await self.get_project(project_id, actor_id)
        actor = await self.projects.get_member(project_id, actor_id)
        if not project.can_manage_members(actor.role) or not project.can_assign_role(actor.role, role):
            raise ProjectAccessDeniedError()
        if await self.projects.get_member(project_id, user_id):
            raise MemberAlreadyExistsError()
        member = await self.projects.add_member(ProjectMember.create(project_id, user_id, role))
        await self.publisher.publish(ProjectMemberAdded(project_id, user_id, role.value, actor_id).envelope())
        return member

    async def members(self, project_id, actor_id):
        await self.get_project(project_id, actor_id)
        return await self.projects.list_members(project_id)

    async def check_membership(self, project_id, user_id):
        if not await self.projects.get(project_id):
            raise ProjectNotFoundError()
        return await self.projects.get_member(project_id, user_id)

    async def remove_member(self, project_id, actor_id, user_id):
        project = await self.get_project(project_id, actor_id)
        actor = await self.projects.get_member(project_id, actor_id)
        target = await self.projects.get_member(project_id, user_id)
        if not target or target.role == ProjectRole.OWNER:
            raise ProjectAccessDeniedError()
        if not project.can_manage_members(actor.role):
            raise ProjectAccessDeniedError()
        if actor.role == ProjectRole.MANAGER and target.role not in {ProjectRole.MEMBER, ProjectRole.VIEWER}:
            raise ProjectAccessDeniedError()
        await self.projects.remove_member(project_id, user_id)

    async def create_invitation(self, project_id, actor_id, invited_user_id, days):
        if invited_user_id == actor_id:
            raise CannotInviteSelfError()
        project = await self.get_project(project_id, actor_id)
        actor = await self.projects.get_member(project_id, actor_id)
        if not project.can_manage_members(actor.role):
            raise ProjectAccessDeniedError()
        if await self.projects.get_member(project_id, invited_user_id):
            raise MemberAlreadyExistsError()
        expires = datetime.now(timezone.utc) + timedelta(days=days)
        invitation = await self.invitations.create(
            ProjectInvitation.create(project_id, invited_user_id, actor_id, expires))
        await self.publisher.publish(
            ProjectInvitationCreated(project_id, invitation.id, invited_user_id, actor_id, expires).envelope())
        return invitation

    async def my_invitations(self, user_id):
        return await self.invitations.list_for_user(user_id)

    async def accept(self, invitation_id, actor_id):
        invitation = await self.invitations.get(invitation_id)
        if not invitation or invitation.invited_user_id != actor_id:
            raise InvitationNotFoundError()
        invitation.accept()
        if await self.projects.get_member(invitation.project_id, actor_id):
            raise MemberAlreadyExistsError()
        member = await self.projects.add_member(
            ProjectMember.create(invitation.project_id, actor_id, ProjectRole.MEMBER))
        await self.invitations.update(invitation)
        await self.publisher.publish(ProjectMemberAdded(invitation.project_id, actor_id, ProjectRole.MEMBER.value,
                                                        invitation.invited_by).envelope())
        return member

    async def decline(self, invitation_id, actor_id):
        invitation = await self.invitations.get(invitation_id)
        if not invitation or invitation.invited_user_id != actor_id:
            raise InvitationNotFoundError()
        invitation.decline()
        return await self.invitations.update(invitation)
