from uuid import UUID
from fastapi import APIRouter
from app.api.dependencies import CurrentUserDep, ProjectServiceDep, SessionDep
from app.schemas.requests import InvitationCreateRequest
from app.schemas.responses import InvitationResponse, MemberResponse

router = APIRouter(tags=["invitations"])


@router.post("/api/v1/projects/{project_id}/invitations", response_model=InvitationResponse, status_code=201)
async def create(project_id: UUID, req: InvitationCreateRequest, user: CurrentUserDep, projects: ProjectServiceDep,
                 db: SessionDep):
    invitation = await projects.create_invitation(project_id, user.id, req.invited_user_id, req.expires_in_days)
    await db.commit()
    return invitation


@router.get("/api/v1/invitations", response_model=list[InvitationResponse])
async def mine(user: CurrentUserDep, projects: ProjectServiceDep):
    return await projects.my_invitations(user.id)


@router.post("/api/v1/invitations/{invitation_id}/accept", response_model=MemberResponse)
async def accept(invitation_id: UUID, user: CurrentUserDep, projects: ProjectServiceDep, db: SessionDep):
    member = await projects.accept(invitation_id, user.id)
    await db.commit()
    return member


@router.post("/api/v1/invitations/{invitation_id}/decline", response_model=InvitationResponse)
async def decline(invitation_id: UUID, user: CurrentUserDep, projects: ProjectServiceDep, db: SessionDep):
    invitation = await projects.decline(invitation_id, user.id)
    await db.commit()
    return invitation
