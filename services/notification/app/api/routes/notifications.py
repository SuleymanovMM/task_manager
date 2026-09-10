from datetime import datetime
from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import get_current_user, get_notification_repo
from app.application.commands.mark_all_read import MarkAllNotificationsReadCommand
from app.application.commands.mark_read import MarkNotificationReadCommand
from app.application.queries.list_notifications import ListNotificationsQuery
from app.domain.enums.notification_type import NotificationType
from app.schemas.responses import NotificationResponse, PaginatedNotifications

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


def _paginated(items, total: int, page: int, page_size: int) -> PaginatedNotifications:
    return PaginatedNotifications(
        items=[NotificationResponse.model_validate(x) for x in items],
        page=page, page_size=page_size, total=total,
        pages=ceil(total / page_size) if total else 0,
    )


@router.get("", response_model=PaginatedNotifications)
async def list_notifications(
    current_user: Annotated[UUID, Depends(get_current_user)],
    repo=Depends(get_notification_repo),
    type: NotificationType | None = Query(None),
    is_read: bool | None = Query(None),
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await ListNotificationsQuery(repo).execute(
        current_user, page=page, page_size=page_size, type=type, is_read=is_read, from_date=from_date, to_date=to_date
    )
    return _paginated(items, total, page, page_size)


@router.get("/unread", response_model=PaginatedNotifications)
async def unread_notifications(
    current_user: Annotated[UUID, Depends(get_current_user)],
    repo=Depends(get_notification_repo),
    type: NotificationType | None = Query(None),
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await ListNotificationsQuery(repo).execute(
        current_user, page=page, page_size=page_size, type=type, is_read=False, from_date=from_date, to_date=to_date
    )
    return _paginated(items, total, page, page_size)


@router.post("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_read(notification_id: UUID, current_user: Annotated[UUID, Depends(get_current_user)], repo=Depends(get_notification_repo)):
    await MarkNotificationReadCommand(repo).execute(notification_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(current_user: Annotated[UUID, Depends(get_current_user)], repo=Depends(get_notification_repo)):
    await MarkAllNotificationsReadCommand(repo).execute(current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
