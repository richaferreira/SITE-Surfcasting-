from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.db.session import get_db
from app.models.enums import RoleCode
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import AdminUserUpdate, UserListResponse, UserResponse
from app.services.user_admin import UserAdminService


router = APIRouter(prefix="/admin/users", tags=["Backoffice - Usuários"])
admin_dependency = require_roles(RoleCode.ADMIN)


@router.get("", response_model=UserListResponse)
def list_users(
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> UserListResponse:
    del admin
    items, total = UserRepository(db).list(offset, limit)
    return UserListResponse(
        items=[UserResponse.from_user(item) for item in items],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
) -> UserResponse:
    del admin
    return UserResponse.from_user(UserAdminService(db).update(user_id, payload))
