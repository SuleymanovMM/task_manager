from uuid import UUID
from fastapi import APIRouter, Response
from app.api.dependencies import CurrentUserDep, SessionDep, TeamServiceDep
from app.schemas.requests import TeamCreateRequest, TeamPatchRequest
from app.schemas.responses import TeamResponse, PaginatedTeams

router = APIRouter(prefix="/api/v1/teams", tags=["teams"])


@router.post("", response_model=TeamResponse, status_code=201)
async def create(req: TeamCreateRequest, user: CurrentUserDep, teams: TeamServiceDep, db: SessionDep):
    result = await teams.create(user.id, req)
    await db.commit()
    return result


@router.get("", response_model=PaginatedTeams)
async def list_teams(user: CurrentUserDep, teams: TeamServiceDep, offset: int = 0, limit: int = 20):
    limit = max(1, min(limit, 100))
    items, total = await teams.list(user.id, offset, limit)
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.get("/{team_id}", response_model=TeamResponse)
async def get(team_id: UUID, user: CurrentUserDep, teams: TeamServiceDep):
    return await teams.get(team_id, user.id)


@router.patch("/{team_id}", response_model=TeamResponse)
async def patch(team_id: UUID, req: TeamPatchRequest, user: CurrentUserDep, teams: TeamServiceDep, db: SessionDep):
    result = await teams.update(team_id, user.id, req)
    await db.commit()
    return result


@router.delete("/{team_id}", status_code=204)
async def delete(team_id: UUID, user: CurrentUserDep, teams: TeamServiceDep, db: SessionDep):
    await teams.delete(team_id, user.id)
    await db.commit()
    return Response(status_code=204)
