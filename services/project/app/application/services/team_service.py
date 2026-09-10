from datetime import datetime, timezone
from app.domain.entities.team import Team
from app.domain.entities.team_member import TeamMember
from app.domain.enums.team_role import TeamRole
from app.domain.exceptions.project_exceptions import TeamNotFoundError, TeamAccessDeniedError


class TeamService:
    def __init__(self, teams):
        self.teams = teams

    async def create(self, actor, req):
        team = await self.teams.create(Team.create(actor, req.name, req.description))
        await self.teams.add_member(TeamMember.create(team.id, actor, TeamRole.OWNER))
        return team

    async def get(self, team_id, actor):
        team = await self.teams.get(team_id)
        if not team:
            raise TeamNotFoundError()
        if not await self.teams.get_member(team_id, actor):
            raise TeamAccessDeniedError()
        return team

    async def list(self, actor, offset, limit):
        return await self.teams.list_for_user(actor, offset, limit)

    async def update(self, team_id, actor, req):
        team = await self.get(team_id, actor)
        member = await self.teams.get_member(team_id, actor)
        if member.role != TeamRole.OWNER:
            raise TeamAccessDeniedError()
        for field, value in req.model_dump(exclude_unset=True).items():
            setattr(team, field, value)
        team.updated_at = datetime.now(timezone.utc)
        return await self.teams.update(team)

    async def delete(self, team_id, actor):
        await self.get(team_id, actor)
        member = await self.teams.get_member(team_id, actor)
        if member.role != TeamRole.OWNER:
            raise TeamAccessDeniedError()
        await self.teams.delete(team_id)
